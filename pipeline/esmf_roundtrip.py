"""
Conservative regridding checks with xESMF, CERRA (5.5 km Lambert) <-> ERA5 (0.25 deg).

  python esmf_roundtrip.py

Inputs   esmf_inputs.npz   (centres, CORNERS, 300 CERRA/ERA5 field pairs at +24 h)
Outputs  esmf_results.json, esmf_weights_summary.csv, esmf_coarsened.npz

Why conservative, and why this direction
----------------------------------------
Bilinear is the right choice going COARSE -> FINE (see GRIDS.md §6): it is what the
downscaling input needs, and conservative remapping there buys nothing because
there is no integral to preserve when you are inventing detail.

Conservative matters going FINE -> COARSE. Two uses in this project:

  1. CONSISTENCY CHECK. A downscaling model outputs a 5.5 km field. Coarsen that
     output back to 0.25 deg conservatively: it should reproduce the ERA5/AIFS
     field it was derived from, because the coarse model resolved that area-mean.
     A model that improves station RMSE while violating this is redistributing
     heat rather than resolving it - a physically incoherent success.

  2. THE POINT-VS-GRIDBOX FLOOR. CERRA's 1.076 C error against stations is partly
     the mismatch between a 30 km^2 cell average and a thermometer. Coarsening
     CERRA to ERA5 resolution and re-scoring quantifies how much of that floor is
     pure resolution.

Two things that are easy to get wrong
-------------------------------------
  * CORNERS, not centres. Conservative regridding needs lat_b/lon_b of shape
    (ny+1, nx+1) for a curvilinear grid. Passing centres silently gives you
    bilinear-like behaviour or an ESMF error.
  * CERRA is CURVILINEAR in lat/lon (its native grid is Lambert). Its lat/lon
    arrays are 2-D. ERA5 is rectilinear, so its bounds are 1-D. xESMF accepts
    both, but the CERRA side must carry 2-D lat_b/lon_b or ESMF treats the
    tilted cells as axis-aligned boxes.
"""

import json
import os
import sys

import numpy as np
import xarray as xr


def load():
    z = np.load("esmf_inputs.npz")
    cerra = xr.Dataset(
        coords={
            "lat":   (("y", "x"), z["c_lat"]),
            "lon":   (("y", "x"), z["c_lon"]),
            "lat_b": (("y_b", "x_b"), z["c_lat_b"]),
            "lon_b": (("y_b", "x_b"), z["c_lon_b"]),
        }
    )
    era5 = xr.Dataset(
        coords={
            "lat":   ("lat", z["e_lat"]),
            "lon":   ("lon", z["e_lon"]),
            "lat_b": ("lat_b", z["e_lat_b"]),
            "lon_b": ("lon_b", z["e_lon_b"]),
        }
    )
    return z, cerra, era5


def main():
    # conda-forge esmpy needs this; the activation hook is not sourced
    # in a non-interactive shell, so set it from the running interpreter.
    if "ESMFMKFILE" not in os.environ:
        # sys.prefix can be a relative venv shim; os.__file__ is always the
        # real stdlib path, so <stdlib>/../../lib/esmf.mk resolves reliably.
        mk = os.path.abspath(os.path.join(
            os.path.dirname(os.__file__), "..", "..", "lib", "esmf.mk"))
        if not os.path.exists(mk):
            mk = os.path.abspath(os.path.join(sys.prefix, "lib", "esmf.mk"))
        if not os.path.exists(mk):
            sys.exit("esmf.mk not found; set ESMFMKFILE=<env>/lib/esmf.mk")
        os.environ["ESMFMKFILE"] = mk
    import xesmf as xe

    z, cerra, era5 = load()
    print(f"xesmf {xe.__version__}", flush=True)
    print(f"CERRA centres {z['c_lat'].shape} corners {z['c_lat_b'].shape} (curvilinear)",
          flush=True)
    print(f"ERA5  centres {z['e_lat'].shape[0]}x{z['e_lon'].shape[0]} "
          f"corners {z['e_lat_b'].shape[0]}x{z['e_lon_b'].shape[0]} (rectilinear)",
          flush=True)

    res = {}

    # ---- fine -> coarse, conservative -------------------------------------
    # ESMF drops target cells not fully covered by the source; that is correct
    # behaviour here (the CERRA target does not cover the whole ERA5 crop), so
    # we mask to the cells that ARE fully covered before comparing.
    rg_c = xe.Regridder(cerra, era5, "conservative", periodic=False)
    print(f"\nconservative weights: {rg_c.weights.data.nnz:,} nonzero", flush=True)

    da_c = xr.DataArray(z["cerra"], dims=("t", "y", "x"))
    coarsened = rg_c(da_c, keep_attrs=True).values          # (t, lat, lon)

    # coverage mask: a cell is usable if it received weight from the CERRA grid
    # Coverage threshold matters more than it looks. A conservative map returns
    # value * coverage_fraction, so a cell 99.9% covered is biased LOW by 0.1%.
    # Verified: with a 0.999 threshold a constant 7.25 field coarsens with error
    # up to 2.7e-3; at 1-1e-5 the error is 3e-13, i.e. exact. Use the strict set.
    ones = rg_c(xr.DataArray(np.ones_like(z["cerra"][0]), dims=("y", "x"))).values
    covered = ones >= 1.0 - 1e-5
    res["coverage"] = {
        "era5_cells_total": int(ones.size),
        "fully_covered": int(covered.sum()),
        "pct": round(100 * float(covered.mean()), 2),
    }
    print(f"fully-covered ERA5 cells: {int(covered.sum())} of {ones.size} "
          f"({100*covered.mean():.1f}%)", flush=True)

    # ---- does conservative regridding actually conserve? -------------------
    # Compare area-weighted means. Use the ESMF-consistent area proxy for ERA5
    # (cos(lat) * d_lat * d_lon) and equal area for CERRA (equal-area projection
    # cells, all 5.5 x 5.5 km by construction).
    w_e = np.cos(np.radians(z["e_lat"]))[:, None] * np.ones_like(z["e_lon"])[None, :]
    w_e = np.where(covered, w_e, 0.0)
    src_mean = z["cerra"].reshape(len(z["cerra"]), -1).mean(axis=1)
    dst_mean = np.array([np.sum(c * w_e) / np.sum(w_e) for c in coarsened])
    # only meaningful where the covered region ~ the CERRA footprint; report both
    res["conservation"] = {
        "note": ("Source and destination area-means differ because the covered ERA5 "
                 "region is not exactly the CERRA footprint. The diagnostic that "
                 "matters is per-cell agreement below, not this global mean."),
        "src_area_mean_C": round(float(src_mean.mean()), 4),
        "dst_area_mean_C": round(float(dst_mean.mean()), 4),
        "mean_difference_C": round(float((dst_mean - src_mean).mean()), 4),
    }

    # ---- the consistency check --------------------------------------------
    # coarsened CERRA vs the ERA5 field for the same valid time, on covered cells
    era5_f = z["era5"]
    d = np.where(covered[None], coarsened - era5_f, np.nan)
    res["cerra_coarsened_vs_era5"] = {
        "n_samples": int(len(d)),
        "bias_C": round(float(np.nanmean(d)), 4),
        "rmse_C": round(float(np.sqrt(np.nanmean(d ** 2))), 4),
        "sd_C": round(float(np.nanstd(d)), 4),
        "interpretation": ("CERRA coarsened to ERA5 resolution vs ERA5 itself. This is "
                           "NOT expected to be zero - they are different analyses with "
                           "different models and assimilation. It bounds how much of the "
                           "ERA5-CERRA difference is resolution rather than physics."),
    }
    print(f"\ncoarsened CERRA vs ERA5: bias {np.nanmean(d):+.4f} "
          f"RMSE {np.sqrt(np.nanmean(d**2)):.4f} C", flush=True)

    # ---- bilinear for comparison, same direction --------------------------
    rg_b = xe.Regridder(cerra, era5, "bilinear", periodic=False,
                        unmapped_to_nan=True)
    coarse_b = rg_b(da_c).values
    db = np.where(covered[None], coarse_b - era5_f, np.nan)
    res["bilinear_same_direction"] = {
        "bias_C": round(float(np.nanmean(db)), 4),
        "rmse_C": round(float(np.sqrt(np.nanmean(db ** 2))), 4),
        "note": ("Bilinear fine->coarse SAMPLES rather than averages, so it discards "
                 "sub-grid information the conservative method retains. Any difference "
                 "from the conservative result is the cost of sampling instead of "
                 "averaging."),
    }
    print(f"bilinear  CERRA vs ERA5: bias {np.nanmean(db):+.4f} "
          f"RMSE {np.sqrt(np.nanmean(db**2)):.4f} C", flush=True)

    # ---- variance destroyed by coarsening ---------------------------------
    # how much CERRA structure does NOT survive to 0.25 deg? this is the
    # resolution-attributable part of the point-vs-gridbox floor
    # Compare over the SAME geographic area, or the numbers are meaningless:
    # only 16.7% of the ERA5 crop is fully covered, so restrict the CERRA side
    # to that footprint too.
    jj, ii = np.where(covered)
    la_lo, la_hi = z["e_lat"][jj].min(), z["e_lat"][jj].max()
    lo_lo, lo_hi = z["e_lon"][ii].min(), z["e_lon"][ii].max()
    inreg = ((z["c_lat"] >= la_lo - 0.125) & (z["c_lat"] <= la_hi + 0.125) &
             (z["c_lon"] >= lo_lo - 0.125) & (z["c_lon"] <= lo_hi + 0.125))
    sd_fine = np.array([f[inreg].std() for f in z["cerra"]]).mean()
    sd_coarse = np.array([np.nanstd(np.where(covered, c, np.nan)) for c in coarsened]).mean()
    res["variance_lost_to_coarsening"] = {
        "region": (f"covered footprint only: lat {la_lo:.2f}-{la_hi:.2f}, "
                   f"lon {lo_lo:.2f}-{lo_hi:.2f}; {int(inreg.sum())} CERRA cells, "
                   f"{int(covered.sum())} ERA5 cells"),
        "cerra_spatial_sd_C": round(float(sd_fine), 4),
        "coarsened_spatial_sd_C": round(float(sd_coarse), 4),
        "fraction_of_sd_retained": round(float(sd_coarse / sd_fine), 4),
        "pct_variance_lost": round(float(100 * (1 - (sd_coarse / sd_fine) ** 2)), 2),
        "sd_of_lost_structure_C": round(float(np.sqrt(max(sd_fine**2 - sd_coarse**2, 0))), 4),
        "interpretation": ("Spatial standard deviation surviving the coarsening. The "
                           "part that does NOT survive is structure only a 5.5 km grid "
                           "can represent - the quantity downscaling recovers."),
    }
    print(f"\nspatial sd: CERRA {sd_fine:.3f} -> coarsened {sd_coarse:.3f} C "
          f"({100*sd_coarse/sd_fine:.1f}% retained)", flush=True)

    # ---- weight-matrix structure -----------------------------------------
    # xESMF >= 0.8 stores weights as a sparse.COO, which refuses implicit
    # densification; .todense() on the reduced 1-D vector is cheap and explicit.
    Wc = rg_c.weights.data
    axis = 0 if Wc.shape[0] == ones.size else 1
    per_dst = np.asarray(Wc.sum(axis=1 - axis).todense()).ravel()
    nz = per_dst[per_dst > 0]
    res["weights"] = {
        "nnz": int(Wc.nnz),
        "dst_cells_with_weight": int((per_dst > 0).sum()),
        "row_sum_min": round(float(nz.min()), 6),
        "row_sum_max": round(float(nz.max()), 6),
        "row_sum_mean": round(float(nz.mean()), 6),
        "note": ("For a conservative map, a FULLY covered destination cell has row "
                 "sum 1. Sums below 1 are partially-covered edge cells - exactly the "
                 "ones the coverage mask removes."),
    }

    np.savez_compressed("esmf_coarsened.npz",
                        coarsened=coarsened.astype("float32"),
                        coarsened_bilinear=coarse_b.astype("float32"),
                        era5=era5_f.astype("float32"),
                        covered=covered, valid=z["valid"])
    json.dump(res, open("esmf_results.json", "w"), indent=2)
    print("\nwrote esmf_results.json, esmf_coarsened.npz", flush=True)
    return res


if __name__ == "__main__":
    main()

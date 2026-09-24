# Aligning the ERA5/AIFS lat-lon grid to CERRA's Lambert grid

Short answer: **one `pyproj` transform, then bilinear sampling in fractional
source-index space.** The sampling map is identical for every timestep, so it is
computed once and reused. No datum conversion is needed and no vector rotation applies.

Everything below was measured, not assumed. Machine-readable: `domain_spec_leningrad.json`.

---

## 1. The two grids

| | ERA5 / AIFS | CERRA |
|---|---|---|
| CRS | geographic lat/lon | Lambert conformal conic |
| Spacing | 0.25° | 5500 m |
| Sphere | — | R = 6371229 m |
| Reference | — | `lat_0=50, lon_0=8, lat_1=lat_2=50` |

```
+proj=lcc +lat_0=50 +lon_0=8 +lat_1=50 +lat_2=50 +x_0=0 +y_0=0 +R=6371229 +units=m +no_defs
```

## 2. There is no datum problem

CERRA is defined on a sphere of radius 6371229 m. The obvious worry is whether feeding
`EPSG:4326` (WGS84 ellipsoid) coordinates into that projection introduces a shift.

**Measured: it does not.** Transforming five points across the domain via `EPSG:4326`
and via `+proj=longlat +R=6371229` gives **identical results to 0.0 m**. `pyproj` treats
the geographic side as spherical when the target is spherical, which is the standard
meteorological convention. Either source CRS string works.

## 3. The alignment is confirmed by the data, not just by the code

A parameter or sign error would be silent — it would just shift everything by kilometres.
The check that catches it: for a 5.5 km grid, no point can be more than
5.5/√2 = **3.889 km** from its nearest cell centre.

| | km |
|---|---|
| Geometric maximum | 3.889 |
| Observed median (83 stations) | **2.098** |
| Expected median, random placement in a cell | 2.196 |
| Observed maximum | **3.668** |

Every one of 83 independently-sourced stations lands inside its own cell, and the median
matches the random-placement expectation. **Run this check after any change to the
projection string.** It is the only cheap test that catches a silent misalignment.

## 4. What actually makes this non-trivial

![ERA5 grid drawn in CERRA's Lambert space, and the resampling comparison]({{artifact:art_e2b03a78-f771-4263-b091-252cd150174e}})

**The lat-lon grid is curved and rotated in Lambert space.** Panel (a) draws it.

- A single latitude row deviates from a straight line by up to **55 km** across the
  input crop.
- **Meridian convergence**: grid north tilts from Lambert north by
  `(lon − 8°) × sin(50°)`, i.e. **8.0° at the western edge and 30.1° at the eastern** —
  22° of variation across the domain. Analytic and measured values agree to **0.00°**,
  confirming the projection parameters are exactly as documented.
- **Cells are anisotropic and latitude-dependent**: 0.25° is 27.8 km north-south
  everywhere but 16.8 km east-west at 53 °N, 13.9 km at 60 °N, and 10.8 km at 67 °N.

Three consequences:

1. **No axis-aligned resampler will work.** `scipy.ndimage.zoom`, `torch.nn.Upsample`,
   `PixelShuffle` all assume a separable, axis-aligned scaling. The mapping here is
   neither separable nor axis-aligned.
2. **The upscale factor is not 5×.** I had this wrong earlier. ~1,227 ERA5 cells cover
   the target box against 15,621 CERRA cells: **12.7× in cells, 3.6× linear** — and
   non-integer, which rules out integer-factor upsampling layers.
3. **2 m temperature is a scalar, so no vector rotation is needed.** If you later
   downscale wind, you must rotate `u`/`v` by the convergence angle above. Getting this
   wrong produces a plausible-looking field with systematically wrong direction.

## 4a. Worked example: St Petersburg

The abstract version above is hard to picture, so here is the same operation carried out
at one real place, for one real forecast — Pulkovo airport (59.8000 °N, 30.2630 °E),
valid 2026-01-01 00 Z at +24 h lead.

![The alignment carried out step by step at St Petersburg]({{artifact:art_62c653c4-2c86-4fac-96ff-4580f97d7388}})

**Panel (a) — the problem, concretely.** The thin blue mesh is CERRA: square, 5.5 km,
axis-aligned because this *is* its native projection. The heavy red boxes are four ERA5
cells. They are tilted about 16° here, and they are not square — 14.0 km east-west against
27.8 km north-south at this latitude, an aspect ratio of 2:1. Nothing about the red mesh
lines up with the blue one, and no amount of `zoom`/`Upsample` will make it.

**Panel (b) — the solution, for one cell.** The CERRA cell containing Pulkovo is at
59.7881 °N, 30.2901 °E, which is **2.04 km** from the station — comfortably inside the
3.889 km geometric bound, which is how we know the projection is right.

Convert that cell centre to a *fractional index* into the ERA5 grid:

```
lat 59.7881 °N  →  source lat index 28.8476   (brackets 60.00 / 59.75 °N)
lon 30.2901 °E  →  source lon index 47.1602   (brackets 30.25 / 30.50 °E)
```

The fractional parts are the weights: `wy = 0.8476`, `wx = 0.1602`. Four neighbours,
four products:

| Neighbour | Weight | ERA5 value |
|---|---|---|
| 60.00 °N, 30.25 °E | 0.1279 | 15.396 °C |
| 60.00 °N, 30.50 °E | 0.0244 | 15.107 °C |
| **59.75 °N, 30.25 °E** | **0.7118** | 14.988 °C |
| 59.75 °N, 30.50 °E | 0.1358 | 15.029 °C |

Weights sum to **1.0000000000**. The result is **15.0485 °C**, matching
`scipy.ndimage.map_coordinates(order=1)` to 3×10⁻⁷ °C. CERRA's own value for that cell is
15.443 °C, so the residual the model has to predict is **+0.395 °C**.

That is the whole operation. The two index arrays are **identical for every timestep**, so
they are computed once and reused for all 3,240 samples — the per-sample cost is one
gather-and-weight.

**Panels (c) and (d) — why it is worth doing.** The same field, same colour scale, same
window. ERA5 provides **13 distinct values** across this area; CERRA resolves **82**. The
Gulf of Finland shoreline (white contour) is visible in CERRA and absent from ERA5 — the
coarse grid steps across the coast in one jump.

Inside the *single* ERA5 cell centred at 59.75 °N, 30.25 °E there are **13 CERRA cells**.
Across the study period they carry a mean within-cell spatial spread of **0.559 °C**, with
a maximum spread of **7.88 °C** — and that one cell spans a land-sea fraction from 0.64 to
1.00 and terrain from 5 m to 99 m. ERA5 reports one number for all of it.

**This is the signal.** Interpolation moves the coarse value onto the fine grid but cannot
invent that structure — it only smooths. Recovering it is exactly what the downscaling
model is for, which is why the interpolation baseline is the number to beat rather than
the answer.

## 5. Recommended approach

```python
import numpy as np, pyproj

CERRA_P = ("+proj=lcc +lat_0=50 +lon_0=8 +lat_1=50 +lat_2=50 "
           "+x_0=0 +y_0=0 +R=6371229 +units=m +no_defs")
fwd = pyproj.Transformer.from_crs("EPSG:4326", CERRA_P, always_xy=True).transform
inv = pyproj.Transformer.from_crs(CERRA_P, "EPSG:4326", always_xy=True).transform

# 1. CERRA native grid from the documented SW corner + spacing
x0, y0 = fwd(-17.4859, 20.2923)              # lon, lat of cell (0, 0)
xg = x0 + np.arange(1069) * 5500.0
yg = y0 + np.arange(1069) * 5500.0

# 2. target window -> lat/lon of every target cell centre
XX, YY = np.meshgrid(xg[707:834], yg[720:843])
tlon, tlat = inv(XX, YY)

# 3. express each target cell as a FRACTIONAL index into the source grid.
#    src_lat descends, so reverse it for np.interp's ascending requirement.
lat_idx = np.interp(tlat, src_lat[::-1], np.arange(len(src_lat))[::-1])
lon_idx = np.interp(tlon % 360, src_lon, np.arange(len(src_lon)))
```

`lat_idx` / `lon_idx` are **constant for every timestep** — compute once, reuse for all
3,240 samples. Saved as `regrid_map.npz`.

Then either:

**CPU / preprocessing** — `scipy.ndimage.map_coordinates(field, [lat_idx, lon_idx],
order=1)`. Verified identical to `RegularGridInterpolator(method="linear")` to **1e-6 °C**.

**Inside the network** — the same file stores `grid_y` / `grid_x` normalised to [−1, 1] for
`torch.nn.functional.grid_sample(x, grid, mode="bilinear", align_corners=True)`. This is
differentiable and runs on GPU, so the regridding becomes a fixed layer rather than a
preprocessing step. Preferred: it keeps the model's input the native 0.25° field, so no
resampled copy is stored and the resampling can never silently drift out of sync with the
target grid.

## 6. Which interpolation

Measured on 400 real +24 h samples, scored against CERRA:

| Method | Baseline RMSE | Cost |
|---|---|---|
| nearest | 1.4690 °C | 0.3 s |
| **bilinear** | **1.4347 °C** | 0.5 s |
| cubic | 1.4409 °C | 3.8 s |

**Use bilinear.** Nearest costs 0.034 °C — about 6 % of the 0.588 °C stage-2 objective,
which is not free. Cubic is *worse* than bilinear despite being higher-order and 8× slower:
it overshoots at the sharp land-water gradients that dominate this domain (its field range
is 6.63–17.49 °C against bilinear's 6.85–17.44 °C for the same input). Higher order is not
better when the truth has near-discontinuities.

> **Separate concern — station extraction.** For comparing a *field* to *point
> observations*, use **nearest cell, not interpolation**. The fields are grid-box averages;
> interpolating between them invents values the dataset never claimed. Bilinear is right
> for field-to-field regridding, nearest is right for field-to-point. The project uses
> both, deliberately, and `COMPARISONS.md` §7 quantifies the difference (0.046 °C).

## 7. Conservative regridding with `xesmf` — the fine → coarse direction

Installed and run: `xesmf 0.9.2` + `esmpy` in the `downscale-esmf` environment.
Script: `esmf_roundtrip.py`. Results: `esmf_results.json`.

**It is the wrong tool for the model input.** Conservative remapping preserves area
integrals, which matters when averaging *down*. Going coarse → fine there is no integral
to preserve — you are inventing detail — so bilinear (§6) stays the choice, and
`grid_sample` additionally keeps the operation differentiable and inside the model, which
`xesmf` cannot.

**It is the right tool for two other jobs**, both fine → coarse.

![Conservative coarsening of CERRA to the ERA5 grid]({{artifact:art_9ebc2650-95ba-47c9-a55e-bf90d188f4aa}})

### Setup, and the two things that break it

```python
import os, sys, numpy as np, xarray as xr
os.environ.setdefault("ESMFMKFILE",                       # see the gotcha below
    os.path.abspath(os.path.join(os.path.dirname(os.__file__), "..", "..",
                                 "lib", "esmf.mk")))
import xesmf as xe

cerra = xr.Dataset(coords={                     # CURVILINEAR: 2-D lat/lon AND 2-D bounds
    "lat":   (("y", "x"),     c_lat),           # (123, 127)
    "lon":   (("y", "x"),     c_lon),
    "lat_b": (("y_b", "x_b"), c_lat_b),         # (124, 128)  <- corners, +1 each dim
    "lon_b": (("y_b", "x_b"), c_lon_b)})
era5 = xr.Dataset(coords={                      # RECTILINEAR: 1-D
    "lat": ("lat", e_lat), "lon": ("lon", e_lon),
    "lat_b": ("lat_b", e_lat_b), "lon_b": ("lon_b", e_lon_b)})

rg = xe.Regridder(cerra, era5, "conservative", periodic=False)   # 28,360 nonzero weights
```

**Gotcha 1 — `ESMFMKFILE`.** The conda-forge `esmpy` build finds ESMF through an
activation hook that a non-interactive shell never sources, so `import xesmf` fails with
`KeyError: 'ESMFMKFILE'`. Set it from inside the script. Note `sys.prefix` can be a
relative venv shim; deriving the path from `os.__file__` is reliable.

**Gotcha 2 — corners, not centres.** Conservative regridding needs `lat_b`/`lon_b` of
shape `(ny+1, nx+1)`. For CERRA, offset by half a cell in *projected* space and then
inverse-transform — the corners are not midpoints of the lat/lon centres, because the
cells are tilted. For ERA5 the bounds are 1-D midpoints extended by half a step.

**Gotcha 3 — the coverage mask threshold.** A conservative map returns
`value × coverage_fraction`, so a partially-covered destination cell is biased *low* in
exact proportion. Regrid a field of ones to get the coverage, then mask. The threshold is
not cosmetic:

| Coverage deficit allowed | Cells kept | Max error on a constant 7.25 °C field |
|---|---|---|
| 10⁻¹ | 1,132 | 0.718 °C |
| 10⁻³ | 1,107 | 2.7 × 10⁻³ °C |
| **10⁻⁵** | **1,104** | **3.3 × 10⁻¹³ °C** |

My first pass used 0.999 and saw a 2.7 × 10⁻³ °C error I nearly reported as "machine
precision". It is not — it is a real low bias on 3 edge cells. Confirmed by the identity
`output = 7.25 × coverage` holding to 4 × 10⁻¹⁵. **Conservation is exact; use 1 − 10⁻⁵.**

### Use 1 — the physical consistency check

A downscaling model emits a 5.5 km field. Coarsen it back conservatively: it should
reproduce the AIFS field it came from, because the coarse model already resolved that
area-mean. A model that improves station RMSE while *failing* this is redistributing heat
rather than resolving it — an incoherent success, and worth catching before you report it.

Establishing the baseline for that check on CERRA itself:

| | Bias | RMSE |
|---|---|---|
| CERRA coarsened → ERA5, **conservative** | −0.196 °C | **1.168 °C** |
| CERRA coarsened → ERA5, bilinear | −0.190 °C | 1.244 °C |

Two readings. First, **conservative beats bilinear by 0.076 °C in this direction** —
bilinear *samples* where conservative *averages*, discarding sub-grid information, which
is exactly why it is the wrong choice going down. Second, 1.168 °C is not small, and it is
not supposed to be zero: ERA5 and CERRA are different models with different assimilation.
It bounds how much of the ERA5–CERRA difference is resolution rather than physics.

### Use 2 — how much structure is resolution-only

Over the covered footprint (15,554 CERRA cells → 1,104 ERA5 cells), coarsening retains
**96.3 % of the spatial standard deviation** — 2.385 → 2.296 °C. The lost part is
**0.645 °C**, i.e. **7.3 % of the spatial variance**.

That 0.645 °C is an independent estimate of the same quantity §4a measured locally: the
within-ERA5-cell spread at St Petersburg was **0.559 °C**. Two different methods, one
global and one local, agreeing to about 0.09 °C. **This is the structure downscaling
exists to recover**, and it sets the scale of the achievable gain — consistent with the
0.400 °C station headroom in `COMPARISONS.md`, which is what survives after CERRA's own
error against point observations.

> Note the asymmetry: 7.3 % of *variance* sounds small, but the target field's variance is
> dominated by the large-scale gradient that ERA5 already has. The relevant comparison is
> 0.645 °C against the 0.588 °C stage-2 objective — the same order, which is why this is
> worth modelling rather than a rounding error.

## 8. Checks to run after any grid change

1. **Corner span**: `(1069 − 1) × 5.5 km` must equal the span implied by the documented
   corner lat/lons. Verified to the metre.
2. **Station offsets**: median ≈ 2.1 km, maximum < 3.889 km, over the full station set.
3. **Round trip**: `inv(fwd(lon, lat))` must return the input to < 1e-6°.
4. **Convergence angle**: measured meridian tilt must equal `(lon − 8) × sin(50°)`.
5. **A real field**: crop one CERRA field, take the cell nearest a known station, and
   compare to that station's observation for the same timestamp. An indexing error puts
   you hundreds of km away, which shows up immediately as an implausible value — this is
   how the original crop was validated (a mid-January +5.6 °C reading in St Petersburg
   looked wrong but matched the station exactly).

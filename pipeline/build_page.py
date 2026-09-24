
import json
geo   = json.load(open("geo_nwr.json"))
stns  = json.load(open("stations_nwr.json"))
payl  = json.load(open("facts_nwr.json"))
F     = payl["facts"]
DATA  = json.dumps({"geo":geo,"stations":stns,**payl}, separators=(",",":"))

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CERRA and downscaling over the Russian Northwest</title>
<style>
:root{
  --bg:#fbfaf8; --ink:#1c2024; --mut:#6b7280; --line:#e2e0dc;
  --ok:#1f6f8b; --goal:#c0392b; --in:#8d959c; --card:#ffffff;
  --land:#eceae5; --water:#ffffff; --sea:#dce9ef; --lake:#dbe9f0;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:56px 28px 96px}
h1{font-size:2.05rem;line-height:1.2;margin:0 0 .5rem;letter-spacing:-.02em;font-weight:650}
.sub{color:var(--mut);font-size:1.06rem;margin:0 0 2.6rem;max-width:60ch}
h2{font-size:1.32rem;margin:3.2rem 0 .5rem;letter-spacing:-.01em;font-weight:640}
h2:first-of-type{margin-top:2.2rem}
h3{font-size:1.02rem;margin:1.8rem 0 .35rem;font-weight:640}
p{margin:.65rem 0;max-width:68ch}
.lede{font-size:1.06rem}
small,.small{font-size:.85rem;color:var(--mut)}
code{background:#f1efeb;padding:.1em .38em;border-radius:4px;font-size:.87em}
hr{border:0;border-top:1px solid var(--line);margin:3rem 0}
a{color:var(--ok)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:20px 22px;margin:1.4rem 0}
.grid{display:grid;gap:14px}
.g3{grid-template-columns:repeat(auto-fit,minmax(184px,1fr))}
.g2{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.stat{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:15px 17px}
.stat .v{font-size:1.5rem;font-weight:660;letter-spacing:-.02em;line-height:1.15}
.stat .l{font-size:.79rem;color:var(--mut);margin-top:3px;line-height:1.4}
.tag{display:inline-block;font-size:.73rem;letter-spacing:.05em;text-transform:uppercase;
  color:var(--mut);border:1px solid var(--line);border-radius:999px;padding:2px 9px;
  background:#fff;margin-bottom:.7rem}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin:.8rem 0}
th,td{text-align:right;padding:8px 10px;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
th{font-weight:620;color:var(--mut);font-size:.79rem;letter-spacing:.02em;
  text-transform:uppercase;border-bottom:1px solid #cfcdc8}
tbody tr:last-child td{border-bottom:0}
.num{font-variant-numeric:tabular-nums}
figure{margin:1.4rem 0}
figcaption{font-size:.85rem;color:var(--mut);margin-top:.6rem;max-width:66ch}
#mapwrap{position:relative;background:var(--card);border:1px solid var(--line);
  border-radius:12px;overflow:hidden}
svg{display:block;width:100%;height:auto;touch-action:none}
.ctl{display:flex;flex-wrap:wrap;gap:7px;padding:12px 14px;border-bottom:1px solid var(--line);
  align-items:center;background:#fdfcfa}
button{font:inherit;font-size:.83rem;background:#fff;color:var(--ink);
  border:1px solid #d6d3ce;border-radius:7px;padding:5px 12px;cursor:pointer;
  transition:background .13s,border-color .13s}
button:hover{background:#f4f2ee}
button[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.ctl .sep{width:1px;height:20px;background:var(--line);margin:0 4px}
#tip{position:absolute;pointer-events:none;background:rgba(28,32,36,.94);color:#fff;
  font-size:.79rem;line-height:1.45;padding:6px 9px;border-radius:6px;opacity:0;
  transition:opacity .1s;white-space:nowrap;z-index:5}
.lg{display:flex;flex-wrap:wrap;gap:16px;padding:11px 15px;border-top:1px solid var(--line);
  font-size:.8rem;color:var(--mut);background:#fdfcfa}
.lg i{display:inline-block;width:11px;height:11px;border-radius:2px;margin-right:5px;
  vertical-align:-1px}
.callout{border-left:3px solid var(--goal);background:#fdf6f5;padding:14px 18px;
  border-radius:0 9px 9px 0;margin:1.5rem 0}
.callout.ok{border-left-color:var(--ok);background:#f2f8fa}
.callout p{margin:.3rem 0}
.callout .h{font-weight:650;font-size:.94rem;margin-bottom:.2rem}
ol,ul{max-width:68ch;padding-left:1.3rem}
li{margin:.4rem 0}
.foot{margin-top:3.5rem;padding-top:1.4rem;border-top:1px solid var(--line);
  font-size:.83rem;color:var(--mut)}
.foot a{color:var(--mut)}
@media(max-width:640px){.wrap{padding:34px 17px 70px}h1{font-size:1.6rem}}
</style></head><body><div class="wrap">

<span class="tag">Project note</span>
<h1>CERRA, and how it becomes a downscaling target for the Russian Northwest</h1>
<p class="sub">What the Copernicus European Regional ReAnalysis actually is, why its grid
reaches your domain, and what it can and cannot serve as ground truth for.</p>

<div class="grid g3">
  <div class="stat"><div class="v">5.5 km</div><div class="l">CERRA horizontal grid spacing</div></div>
  <div class="stat"><div class="v">1984&ndash;2026</div><div class="l">Coverage, still extending</div></div>
  <div class="stat"><div class="v">664 km</div><div class="l">Clearance from your stations to CERRA's eastern edge</div></div>
  <div class="stat"><div class="v">5.1&times;</div><div class="l">Downscaling factor from 0.25&deg; input</div></div>
</div>

<h2>1. What CERRA is</h2>
<p class="lede">CERRA is a <strong>regional reanalysis</strong>: a physically consistent
reconstruction of past weather over Europe, produced by running a limited-area NWP model
and forcing it to stay close to observations through data assimilation. It is not a
forecast and not an interpolation of station data &mdash; it is a model state corrected
by observations, on a fixed grid, every three hours.</p>

<div class="card">
<h3 style="margin-top:0">The system, in one paragraph</h3>
<p style="margin-bottom:0">CERRA is built on the <strong>HARMONIE-ALADIN</strong> data
assimilation system developed within the ACCORD consortium, running at 5.5 km with
<strong>106 vertical levels</strong>. It assimilates observations using
<strong>3D-Var</strong> across <strong>eight cycles per day</strong> (00, 03, 06, 09, 12,
15, 18, 21 UTC). Its background error covariances come from a separate
<strong>10-member ensemble of data assimilation</strong> (CERRA-EDA) run at 11 km. Lateral
boundary conditions come from <strong>ERA5</strong> &mdash; so CERRA is, in effect, ERA5
given a much finer regional model and a denser observation set.</p>
</div>

<p>That last point is the one that matters for downscaling. CERRA and ERA5 are not
independent datasets: ERA5 supplies CERRA's boundaries and constrains its large scales.
The information CERRA <em>adds</em> is regional &mdash; finer terrain, resolved lakes and
coastlines, denser local observations. That added information is exactly what a
downscaling model can learn to reproduce.</p>

<h3>The three components</h3>
<table>
<thead><tr><th>Component</th><th>Resolution</th><th>Role</th></tr></thead>
<tbody>
<tr><td><strong>CERRA</strong></td><td class="num">5.5 km</td><td style="text-align:left">Main 3-D atmospheric reanalysis</td></tr>
<tr><td><strong>CERRA-EDA</strong></td><td class="num">11 km</td><td style="text-align:left">10-member ensemble; supplies flow-dependent background errors</td></tr>
<tr><td><strong>CERRA-Land</strong></td><td class="num">5.5 km</td><td style="text-align:left">Separate 2-D surface reanalysis</td></tr>
</tbody></table>

<h2>2. Does its grid actually reach the Russian Northwest?</h2>
<p>This was the open question in the literature review, and it needed checking rather than
assuming: CERRA is distributed on a Lambert conformal conic grid, and the lat/lon bounding
box quoted for projected grids is misleading &mdash; it describes a rectangle in projected
space, not in geography. The honest test is to transform the target domain into CERRA's own
projection and check containment there.</p>

<div id="mapwrap">
  <div class="ctl">
    <button id="b-dom"   aria-pressed="true">CERRA domain</button>
    <button id="b-box"   aria-pressed="true">Target domain</button>
    <button id="b-stn"   aria-pressed="true">Stations</button>
    <span class="sep"></span>
    <button id="b-g28">0.25&deg; grid</button>
    <button id="b-g55">5.5 km grid</button>
    <span class="sep"></span>
    <button id="b-zoom" aria-pressed="false">Zoom to domain</button>
  </div>
  <svg id="map" viewBox="0 0 900 620" role="img"
       aria-label="Map of the CERRA domain, the target domain over the Russian Northwest, and 144 observing stations"></svg>
  <div id="tip" role="status"></div>
  <div class="lg">
    <span><i style="background:var(--ok)"></i>CERRA 5.5 km domain</span>
    <span><i style="background:var(--goal)"></i>Target domain &amp; stations</span>
    <span><i style="background:var(--lake);border:1px solid #b9ccd6"></i>Lakes</span>
    <span id="lg-grid" style="display:none"><i style="background:#b9b6b0"></i><span id="lg-grid-t"></span></span>
  </div>
</div>
<p class="small" style="margin-top:.7rem">Drag to pan, scroll or pinch to zoom, hover a
station for its name and elevation. Grid overlays are drawn to true scale in CERRA's
projection &mdash; toggle both to see the resolution gap directly.</p>

<div class="callout ok">
<p class="h">The domain is comfortably inside</p>
<p>All <strong>144 stations</strong> fall within the CERRA grid, the nearest sitting
<strong>467 km</strong> from any edge and <strong>664 km</strong> from the eastern
boundary. The target box itself clears the eastern edge by <strong>607 km</strong> and the
northern edge by <strong>219 km</strong>. Nothing about the geometry is marginal.</p>
</div>

<h3>Why the bounding box misleads</h3>
<p>CERRA's grid is a 1069 &times; 1069 square of 5.5 km cells &mdash; 5874 km on a side &mdash;
centred on 8&deg;E at 50&deg;N. Because it is a conic projection, the grid's corners reach
much further east at high latitude than a naive lat/lon box suggests. The documented corner
coordinates make this concrete:</p>
<table>
<thead><tr><th>Corner</th><th>Latitude</th><th>Longitude</th></tr></thead>
<tbody>
<tr><td>Upper&#8209;left</td><td class="num">63.77&deg;N</td><td class="num">58.11&deg;W</td></tr>
<tr><td>Upper&#8209;right</td><td class="num">63.77&deg;N</td><td class="num">74.11&deg;E</td></tr>
<tr><td>Lower&#8209;right</td><td class="num">20.29&deg;N</td><td class="num">33.49&deg;E</td></tr>
<tr><td>Lower&#8209;left</td><td class="num">20.29&deg;N</td><td class="num">17.49&deg;W</td></tr>
</tbody></table>
<p class="small">The upper-right corner reaches 74&deg;E &mdash; past the Urals &mdash;
while the lower-right stops at 33&deg;E. A single &ldquo;eastern limit&rdquo; does not exist
for this grid, which is why the metadata reading of ~35&deg;E was misleading rather than
informative.</p>

<h2>3. Why 5.5 km is the right target, and 2 km is not (yet)</h2>
<p>The appeal of a 2 km product is obvious, but a supervised downscaling model needs a
<em>training target</em> at that resolution, and no open gridded 2 km analysis covers the
Russian Northwest. CERRA does, hourly-to-3-hourly, for four decades. That difference decides
the project shape.</p>

<div class="grid g2">
<div class="card"><h3 style="margin-top:0;color:var(--ok)">AIFS 0.25&deg; &rarr; CERRA 5.5 km</h3>
<p style="margin-bottom:.3rem"><strong>5.1&times;</strong> refinement, with 40 years of
gridded truth to train against and verify on.</p>
<p class="small" style="margin:0">Feasible on modest hardware; standard verification available.</p></div>
<div class="card"><h3 style="margin-top:0;color:var(--goal)">AIFS 0.25&deg; &rarr; 2 km</h3>
<p style="margin-bottom:.3rem"><strong>13.9&times;</strong> refinement, with
<strong>no gridded target</strong> over the domain.</p>
<p class="small" style="margin:0">Viable only as a station-based product, where the 144
stations are themselves the truth.</p></div>
</div>

<h3>What the extra resolution actually buys: the lakes</h3>
<p>This region's forecast difficulty is substantially a lake and coastline problem &mdash;
Ladoga, Onega, Saimaa, the Gulf of Finland. Resolution determines whether those water bodies
exist in the model at all:</p>
<table>
<thead><tr><th>Lake</th><th>Area</th><th>Cells at 0.25&deg;</th><th>Cells at 5.5 km</th><th>Cells at 2 km</th></tr></thead>
<tbody id="laketab"></tbody></table>
<p class="small">Lake Ladoga is Europe's largest lake. At 0.25&deg; it is roughly 23 grid
cells &mdash; enough to exist, not enough to shape a lake breeze or an ice margin. At 5.5 km
it is about 584 cells, which is a resolved water body with its own boundary layer.</p>

<h2>4. How CERRA gets used here</h2>
<p>The plan pairs CERRA with two different inputs, for two different purposes. Getting this
distinction right is the difference between a model that generalises and one that only
looks good in validation.</p>

<h3>Stage 1 &mdash; pretrain: ERA5 &rarr; CERRA</h3>
<p>Learn pure spatial refinement from coarse reanalysis to fine reanalysis. About
<strong>122,000</strong> three-hourly analysis times back to 1984 (121,984 at eight
per day for 1984-09-01 to 2026-05-31). Both sides are analyses,
so the input carries almost no forecast error &mdash; the model learns terrain, lakes and
coastline effects without having to also learn bias correction.</p>

<h3>Stage 2 &mdash; fine-tune: AIFS ENS &rarr; CERRA</h3>
<p>Adapt to real forecast error. This is the mapping actually needed at runtime, but AIFS ENS
has only been operational since 25 February 2025 &mdash; about <strong>3,700</strong>
analysis times up to CERRA's 2026-05-31 end, some <strong>33&times; less data</strong>
than stage 1. Too little to train from scratch;
enough to adapt a pretrained model.</p>

<div class="callout">
<p class="h">The failure mode this ordering avoids</p>
<p>A model trained only on ERA5&rarr;CERRA has never seen a forecast be wrong. Feed it a real
AIFS forecast and it will sharpen an incorrect field into a confidently incorrect
high-resolution field &mdash; sharper, and no more accurate. Fine-tuning on genuine
forecast&ndash;truth pairs is what teaches it the difference.</p>
</div>

<div class="callout">
<p class="h">The verification trap</p>
<p>ERA5 assimilates these stations, and CERRA assimilates them too. Verifying against the
same stations the training targets already absorbed will flatter the result. Stations must
be held out <strong>spatially</strong> &mdash; train on one subset, verify on stations the
model has never seen &mdash; not merely split by time.</p>
</div>

<h2>5. What still needs checking</h2>
<p>One assumption underpins all of the above and has <em>not</em> been tested: that CERRA is
an adequate truth over this particular terrain. CERRA is a 5.5 km model constrained by a
sparse observation network in northwest Russia, and its own error against the stations may
be comparable to the AIFS error the project aims to remove. If so, gridded training at
5.5 km is not viable and the station-only path becomes the whole project.</p>
<p>The test is cheap and comes first: pull CERRA 2 m temperature for a year, match it to the
144 stations, and examine the error distribution. If CERRA's station-scale RMSE sits well
below the AIFS error, the plan holds.</p>

<h3>Known limitations worth carrying forward</h3>
<ul>
<li><strong>Cadence.</strong> Analyses are 3-hourly, not hourly. Hourly fields exist only in
the short forecast steps, which is a messier thing to pair against.</li>
<li><strong>Not independent of ERA5.</strong> ERA5 supplies CERRA's lateral boundaries and
constrains its large scales, so the two share error structure at synoptic scale.</li>
<li><strong>Documented GRIB metadata issues.</strong> The product guide records incorrect
step-range metadata for maximum/minimum 2 m temperature and 10 m wind gust.</li>
<li><strong>Observation density.</strong> A regional reanalysis is only as sharp as the
observations it assimilates; coverage over northwest Russia is thinner than over Fennoscandia.</li>
</ul>

<div class="foot">
<p>Geometry, margins, cell counts and lake areas on this page were computed from CERRA's
documented projection parameters (Lambert conformal conic, central meridian 8&deg;,
standard parallels 50&deg;/50&deg;, spherical Earth <span class="num">R = 6 371 229 m</span>)
and the documented corner coordinates, then verified to close against
1068 &times; 5.5 km = 5874 km on both axes. Coverage dates come from the Copernicus Climate
Data Store dataset constraints. System description from the
<a href="https://confluence.ecmwf.int/x/WFQ7E">CERRA product user guide</a>.
Coastlines and lakes: Natural Earth 10 m. Station coordinates: 144 stations in the project's
own metadata table.</p>
<p><strong>Note on dates.</strong> The product user guide's metadata section still states
coverage ending 2021-06-30; the Data Store's own constraints list months through May 2026.
The constraints are authoritative &mdash; the guide text is stale.</p>
</div>

</div>
<script>
const D = __DATA__;
(function(){
const F=D.facts, SVG=document.getElementById("map"), NS="http://www.w3.org/2000/svg";
const W=900,H=620, tip=document.getElementById("tip");

// ---- CERRA Lambert conformal conic, spherical earth (matches documented params) ----
const R=6371229, lon0=8*Math.PI/180, phi0=50*Math.PI/180, DEG=Math.PI/180;
const nCone=Math.sin(phi0);
const Fc=Math.cos(phi0)*Math.pow(Math.tan(Math.PI/4+phi0/2),nCone)/nCone;
const rho0=R*Fc/Math.pow(Math.tan(Math.PI/4+phi0/2),nCone);
function proj(lon,lat){
  const p=lat*DEG, l=(lon-8)*DEG;
  const rho=R*Fc/Math.pow(Math.tan(Math.PI/4+p/2),nCone);
  const th=nCone*l;
  return [rho*Math.sin(th), rho0-rho*Math.cos(th)];
}
// fit: full CERRA square is +-2937 km
const HALF=2937000;
let view={cx:0, cy:0, scale:1};
const BASE=Math.min(W,H)/(2*HALF*1.06);
function sxy(lon,lat){
  const [px,py]=proj(lon,lat);
  const s=BASE*view.scale;
  return [W/2+(px-view.cx)*s, H/2+(py-view.cy)*s*-1];
}
function path(coords){
  let d="";
  for(const ring of coords){
    ring.forEach((c,i)=>{const [X,Y]=sxy(c[0],c[1]); d+=(i?"L":"M")+X.toFixed(1)+" "+Y.toFixed(1);});
  }
  return d;
}
function mk(t,at){const e=document.createElementNS(NS,t);for(const k in at)e.setAttribute(k,at[k]);return e;}

const defs=mk("defs",{});
const gLand=mk("g",{}), gGrid=mk("g",{"clip-path":"url(#boxclip)"}),
      gDom=mk("g",{}), gStn=mk("g",{}), gBar=mk("g",{});
SVG.append(defs,gLand,gGrid,gDom,gStn,gBar);
const GWIN={lon:[29.3,33.3], lat:[59.7,61.9]};   // Lake Ladoga
function ring(lon,lat,N){
  const r=[];
  for(let i=0;i<=N;i++) r.push([lon[0]+(lon[1]-lon[0])*i/N, lat[0]]);
  for(let i=0;i<=N;i++) r.push([lon[1], lat[0]+(lat[1]-lat[0])*i/N]);
  for(let i=0;i<=N;i++) r.push([lon[1]-(lon[1]-lon[0])*i/N, lat[1]]);
  for(let i=0;i<=N;i++) r.push([lon[0], lat[1]-(lat[1]-lat[0])*i/N]);
  return r;
}
function boxRing(N){
  const B=F.domain_box, ring=[];
  for(let i=0;i<=N;i++) ring.push([B.lon[0]+(B.lon[1]-B.lon[0])*i/N, B.lat[0]]);
  for(let i=0;i<=N;i++) ring.push([B.lon[1], B.lat[0]+(B.lat[1]-B.lat[0])*i/N]);
  for(let i=0;i<=N;i++) ring.push([B.lon[1]-(B.lon[1]-B.lon[0])*i/N, B.lat[1]]);
  for(let i=0;i<=N;i++) ring.push([B.lon[0], B.lat[1]-(B.lat[1]-B.lat[0])*i/N]);
  return ring;
}

const show={dom:true,box:true,stn:true,g28:false,g55:false};

function draw(){
  [gLand,gGrid,gDom,gStn,gBar].forEach(g=>{while(g.firstChild)g.removeChild(g.firstChild);});
  // background
  gLand.append(mk("rect",{x:0,y:0,width:W,height:H,fill:"var(--sea)"}));
  for(const f of D.geo.features){
    if(f.properties.k!=="land") continue;
    const g=f.geometry;
    const polys = g.type==="Polygon" ? [g.coordinates] : g.coordinates;
    for(const p of polys){
      const d=path(p); if(!d) continue;
      gLand.append(mk("path",{d,fill:"var(--land)",stroke:"none"}));
    }
  }

  // coast + lakes
  for(const f of D.geo.features){
    const g=f.geometry, k=f.properties.k;
    if(k==="land") continue;
    const polys = g.type==="Polygon" ? [g.coordinates] :
                  g.type==="MultiPolygon" ? g.coordinates :
                  g.type==="LineString" ? [[g.coordinates]] :
                  g.type==="MultiLineString" ? g.coordinates.map(c=>[c]) : [];
    for(const p of polys){
      const d=path(g.type.includes("Polygon")?p:p);
      if(!d) continue;
      if(k==="coast") gLand.append(mk("path",{d,fill:"none",stroke:"#c3bfb8","stroke-width":.8}));
      else gLand.append(mk("path",{d,fill:"var(--lake)",stroke:"#b9ccd6","stroke-width":.5,
            "data-name":f.properties.name||"",
            "data-area":f.properties.area||""}));
    }
  }

  // grid overlays (drawn only inside the target box, to true scale)
  const B=F.domain_box;
  function gridLines(km,col,op){
    const step=km*1000;
    const c0=proj(B.lon[0],B.lat[0]), c1=proj(B.lon[1],B.lat[1]),
          c2=proj(B.lon[1],B.lat[0]), c3=proj(B.lon[0],B.lat[1]);
    const xs=[c0[0],c1[0],c2[0],c3[0]], ys=[c0[1],c1[1],c2[1],c3[1]];
    const xa=Math.min(...xs), xb=Math.max(...xs), ya=Math.min(...ys), yb=Math.max(...ys);
    const g=mk("g",{});
    const px=BASE*view.scale*step;
    if(px<1.4) return g;                     // don't draw an unreadable mesh
    for(let x=Math.ceil(xa/step)*step;x<=xb;x+=step){
      const s=BASE*view.scale;
      const X=W/2+(x-view.cx)*s;
      const Y0=H/2+(ya-view.cy)*s*-1, Y1=H/2+(yb-view.cy)*s*-1;
      g.append(mk("line",{x1:X,y1:Y0,x2:X,y2:Y1,stroke:col,"stroke-width":.4,opacity:op}));
    }
    for(let y=Math.ceil(ya/step)*step;y<=yb;y+=step){
      const s=BASE*view.scale;
      const Y=H/2+(y-view.cy)*s*-1;
      const X0=W/2+(xa-view.cx)*s, X1=W/2+(xb-view.cx)*s;
      g.append(mk("line",{x1:X0,y1:Y,x2:X1,y2:Y,stroke:col,"stroke-width":.4,opacity:op}));
    }
    return g;
  }
  while(defs.firstChild) defs.removeChild(defs.firstChild);
  const cp=mk("clipPath",{id:"boxclip"});
  cp.append(mk("path",{d:path([ring(GWIN.lon,GWIN.lat,40)])}));
  defs.append(cp);
  if(show.g28||show.g55)
    gDom.append(mk("path",{d:path([ring(GWIN.lon,GWIN.lat,40)]),fill:"none",
      stroke:"#9aa3ad","stroke-width":1,"stroke-dasharray":"5 3"}));
  if(show.g28) gGrid.append(gridLines(F.resolution.era5_km,"#33393f",1.3));
  if(show.g55) gGrid.append(gridLines(F.resolution.cerra_km,"#1f6f8b",.7));

  // CERRA domain outline
  if(show.dom){
    const d=path([D.cerra_outline]);
    gDom.append(mk("path",{d,fill:"var(--ok)","fill-opacity":.05,
      stroke:"var(--ok)","stroke-width":1.6}));
  }
  // target box
  if(show.box){
    gDom.append(mk("path",{d:path([boxRing(60)]),fill:"var(--goal)","fill-opacity":.045,
      stroke:"var(--goal)","stroke-width":1.7}));
  }
  // scale bar: pick a round distance that renders 70-190 px
  {
    const ppm=BASE*view.scale;
    const cands=[10,25,50,100,200,500,1000,2000];
    let km=cands.find(k=>k*1000*ppm>=70 && k*1000*ppm<=190);
    if(!km) km = cands.reduce((a,b)=>
      Math.abs(b*1000*ppm-120)<Math.abs(a*1000*ppm-120)?b:a);
    const L=km*1000*ppm, X=22, Y=H-24;
    gBar.append(mk("rect",{x:X-7,y:Y-19,width:L+14,height:29,fill:"#fff",
      "fill-opacity":.82,stroke:"none",rx:4}));
    gBar.append(mk("line",{x1:X,y1:Y,x2:X+L,y2:Y,stroke:"#1c2024","stroke-width":1.5}));
    for(const xx of [X,X+L])
      gBar.append(mk("line",{x1:xx,y1:Y-4,x2:xx,y2:Y+4,stroke:"#1c2024","stroke-width":1.5}));
    const t=mk("text",{x:X+L/2,y:Y-7,"text-anchor":"middle","font-size":10.5,
      fill:"#1c2024","font-family":"inherit"});
    t.textContent=km.toLocaleString()+" km";
    gBar.append(t);
  }

  // stations
  if(show.stn){
    const r = view.scale>3 ? 2.6 : view.scale>1.6 ? 2.0 : 1.6;
    for(const s of D.stations){
      const [X,Y]=sxy(s.lon,s.lat);
      if(X<-20||X>W+20||Y<-20||Y>H+20) continue;
      const c=mk("circle",{cx:X.toFixed(1),cy:Y.toFixed(1),r,fill:"var(--goal)",
                 "fill-opacity":.9,stroke:"none"});
      c.addEventListener("mouseenter",ev=>{
        tip.textContent = s.n + (s.e!=null? "  \u00b7  "+s.e+" m":"");
        tip.style.opacity=1;
      });
      c.addEventListener("mousemove",ev=>{
        const b=SVG.getBoundingClientRect();
        tip.style.left=(ev.clientX-b.left+11)+"px";
        tip.style.top=(ev.clientY-b.top-9)+"px";
      });
      c.addEventListener("mouseleave",()=>{tip.style.opacity=0;});
      gStn.append(c);
    }
  }
}

// ---- controls ----
const bz=document.getElementById("b-zoom");
function bind(id,key,after){
  const b=document.getElementById(id);
  b.addEventListener("click",()=>{
    show[key]=!show[key];
    b.setAttribute("aria-pressed",show[key]?"true":"false");
    if(after)after();
    draw();
  });
}
bind("b-dom","dom"); bind("b-box","box"); bind("b-stn","stn");
function gridLegend(){
  const on=show.g28||show.g55, el=document.getElementById("lg-grid");
  el.style.display = on?"inline":"none";
  document.getElementById("lg-grid-t").textContent =
    show.g28&&show.g55 ? "0.25\u00b0 and 5.5 km grids" :
    show.g28 ? "0.25\u00b0 grid (27.8 km)" : show.g55 ? "5.5 km grid" : "";
}
function ensureLegible(){
  // a mesh needs ~5 px per cell to read; zoom into the lake district if too coarse
  if(!(show.g55||show.g28)) return;
  const r=ring(GWIN.lon,GWIN.lat,20).map(p=>proj(p[0],p[1]));
  const xs=r.map(p=>p[0]), ys=r.map(p=>p[1]);
  const gw=Math.max(...xs)-Math.min(...xs), gh=Math.max(...ys)-Math.min(...ys);
  const need = Math.min(W/(gw*1.5), H/(gh*1.25))/BASE;
  if(view.scale < need*0.9){
    const c=[(Math.max(...xs)+Math.min(...xs))/2,(Math.max(...ys)+Math.min(...ys))/2];
    view={cx:c[0],cy:c[1],scale:need};
    zoomed=true; bz.setAttribute("aria-pressed","true");
    bz.textContent="Zoom out to Europe";
  }
}
bind("b-g28","g28",()=>{gridLegend();ensureLegible();});
bind("b-g55","g55",()=>{gridLegend();ensureLegible();});

let zoomed=false;
bz.addEventListener("click",()=>{
  zoomed=!zoomed;
  bz.setAttribute("aria-pressed",zoomed?"true":"false");
  bz.textContent = zoomed? "Zoom out to Europe" : "Zoom to domain";
  if(zoomed){
    const B=F.domain_box;
    const c=proj((B.lon[0]+B.lon[1])/2,(B.lat[0]+B.lat[1])/2);
    const a=proj(B.lon[0],B.lat[0]), b2=proj(B.lon[1],B.lat[1]);
    const w=Math.abs(b2[0]-a[0]), h=Math.abs(b2[1]-a[1]);
    view={cx:c[0],cy:c[1],scale:Math.min(W/(w*1.5),H/(h*1.35))/BASE};
  } else view={cx:0,cy:0,scale:1};
  draw();
});

// pan / zoom
let drag=null;
SVG.addEventListener("pointerdown",e=>{drag={x:e.clientX,y:e.clientY,cx:view.cx,cy:view.cy};
  SVG.setPointerCapture(e.pointerId);});
SVG.addEventListener("pointermove",e=>{
  if(!drag)return;
  const s=BASE*view.scale;
  view.cx=drag.cx-(e.clientX-drag.x)/s*(W/SVG.getBoundingClientRect().width);
  view.cy=drag.cy+(e.clientY-drag.y)/s*(W/SVG.getBoundingClientRect().width);
  draw();
});
SVG.addEventListener("pointerup",()=>{drag=null;});
SVG.addEventListener("wheel",e=>{
  e.preventDefault();
  const f=Math.exp(-e.deltaY*0.0016);
  view.scale=Math.max(0.75,Math.min(60,view.scale*f));
  draw();
},{passive:false});

// lake table
const tb=document.getElementById("laketab");
for(const l of F.lakes){
  const tr=document.createElement("tr");
  tr.innerHTML = "<td>"+l.name+"</td><td class='num'>"+l.area.toLocaleString()+
    " km&sup2;</td><td class='num'>"+l.era5+"</td><td class='num'>"+
    l.cerra.toLocaleString()+"</td><td class='num'>"+l.goal.toLocaleString()+"</td>";
  tb.append(tr);
}
draw();
})();
</script></body></html>
"""
open("cerra_nw_russia.html","w").write(HTML.replace("__DATA__", DATA))
print("wrote cerra_nw_russia.html")

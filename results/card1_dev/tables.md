# Station scores per lead

Comparison B: 83 scored SYNOP stations, temporal folds 0 1 2, valid 2025-07-02 to 2025-09-12. ME = forecast - obs; a point row's CRPS is its MAE; dressed = N(mean, AIFS spread at the 0.25 deg cell); spread/RMSE = sqrt(mean(s^2)(M+1)/M)/RMSE with s^2 the unbiased member variance (stored spread^2 x M/(M-1)), M = 51.

## Lead +0 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 8501 | 0.005 | 1.755 | 1.086 | 0.325 |
| bilinear | point | 8501 | 0.012 | 1.718 | 1.267 |  |
| bilinear dressed | dressed | 8501 | 0.012 | 1.718 | 1.064 | 0.331 |
| surface (40 km ring) | point | 8501 | -0.108 | 1.638 | 1.222 |  |
| surface (40 km ring) dressed | dressed | 8501 | -0.108 | 1.638 | 1.018 | 0.348 |
| CNN v0 | point | 8501 | 0.029 | 1.743 | 1.282 |  |
| CNN v0 dressed | dressed | 8501 | 0.029 | 1.743 | 1.078 | 0.327 |
| lookup own cell (not held out) | point | 8501 | -0.199 | 1.625 | 1.228 |  |
| lookup own cell (not held out) dressed | dressed | 8501 | -0.199 | 1.625 | 1.023 | 0.350 |
| CERRA (ceiling) | point | 8501 | -0.132 | 1.233 | 0.864 |  |
| CERRA (ceiling) dressed | dressed | 8501 | -0.132 | 1.233 | 0.694 | 0.462 |

## Lead +24 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 8336 | -0.021 | 1.655 | 0.921 | 0.563 |
| bilinear | point | 8336 | -0.019 | 1.610 | 1.180 |  |
| bilinear dressed | dressed | 8336 | -0.019 | 1.610 | 0.891 | 0.579 |
| surface (40 km ring) | point | 8336 | -0.113 | 1.586 | 1.167 |  |
| surface (40 km ring) dressed | dressed | 8336 | -0.113 | 1.586 | 0.878 | 0.588 |
| CNN v0 | point | 8336 | -0.027 | 1.678 | 1.236 |  |
| CNN v0 dressed | dressed | 8336 | -0.027 | 1.678 | 0.940 | 0.556 |
| lookup own cell (not held out) | point | 8336 | -0.200 | 1.538 | 1.141 |  |
| lookup own cell (not held out) dressed | dressed | 8336 | -0.200 | 1.538 | 0.854 | 0.606 |
| CERRA (ceiling) | point | 8336 | -0.134 | 1.233 | 0.863 |  |
| CERRA (ceiling) dressed | dressed | 8336 | -0.134 | 1.233 | 0.644 | 0.756 |

## Lead +48 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 8170 | 0.044 | 1.760 | 0.976 | 0.629 |
| bilinear | point | 8170 | 0.046 | 1.719 | 1.275 |  |
| bilinear dressed | dressed | 8170 | 0.046 | 1.719 | 0.947 | 0.644 |
| surface (40 km ring) | point | 8170 | -0.013 | 1.695 | 1.260 |  |
| surface (40 km ring) dressed | dressed | 8170 | -0.013 | 1.695 | 0.933 | 0.653 |
| CNN v0 | point | 8170 | 0.043 | 1.789 | 1.333 |  |
| CNN v0 dressed | dressed | 8170 | 0.043 | 1.789 | 0.997 | 0.619 |
| lookup own cell (not held out) | point | 8170 | -0.101 | 1.644 | 1.230 |  |
| lookup own cell (not held out) dressed | dressed | 8170 | -0.101 | 1.644 | 0.905 | 0.673 |
| CERRA (ceiling) | point | 8170 | -0.134 | 1.233 | 0.863 |  |
| CERRA (ceiling) dressed | dressed | 8170 | -0.134 | 1.233 | 0.644 | 0.898 |

## Lead +72 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 8004 | 0.090 | 1.912 | 1.064 | 0.701 |
| bilinear | point | 8004 | 0.090 | 1.876 | 1.413 |  |
| bilinear dressed | dressed | 8004 | 0.090 | 1.876 | 1.038 | 0.714 |
| surface (40 km ring) | point | 8004 | 0.042 | 1.848 | 1.396 |  |
| surface (40 km ring) dressed | dressed | 8004 | 0.042 | 1.848 | 1.021 | 0.725 |
| CNN v0 | point | 8004 | 0.091 | 1.933 | 1.459 |  |
| CNN v0 dressed | dressed | 8004 | 0.091 | 1.933 | 1.076 | 0.693 |
| lookup own cell (not held out) | point | 8004 | -0.048 | 1.802 | 1.367 |  |
| lookup own cell (not held out) dressed | dressed | 8004 | -0.048 | 1.802 | 0.994 | 0.744 |
| CERRA (ceiling) | point | 8004 | -0.135 | 1.239 | 0.867 |  |
| CERRA (ceiling) dressed | dressed | 8004 | -0.135 | 1.239 | 0.656 | 1.082 |

## Lead +120 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 7672 | 0.022 | 2.291 | 1.280 | 0.847 |
| bilinear | point | 7672 | 0.022 | 2.268 | 1.758 |  |
| bilinear dressed | dressed | 7672 | 0.022 | 2.268 | 1.264 | 0.855 |
| surface (40 km ring) | point | 7672 | 0.028 | 2.245 | 1.738 |  |
| surface (40 km ring) dressed | dressed | 7672 | 0.028 | 2.245 | 1.248 | 0.864 |
| CNN v0 | point | 7672 | 0.044 | 2.297 | 1.773 |  |
| CNN v0 dressed | dressed | 7672 | 0.044 | 2.297 | 1.280 | 0.844 |
| lookup own cell (not held out) | point | 7672 | -0.057 | 2.215 | 1.720 |  |
| lookup own cell (not held out) dressed | dressed | 7672 | -0.057 | 2.215 | 1.231 | 0.876 |
| CERRA (ceiling) | point | 7672 | -0.134 | 1.250 | 0.874 |  |
| CERRA (ceiling) dressed | dressed | 7672 | -0.134 | 1.250 | 0.718 | 1.551 |

## Lead +168 h

| forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---|---|---:|---:|---:|---:|---:|
| AIFS ENS | ensemble | 7341 | -0.426 | 2.846 | 1.596 | 0.847 |
| bilinear | point | 7341 | -0.423 | 2.833 | 2.214 |  |
| bilinear dressed | dressed | 7341 | -0.423 | 2.833 | 1.588 | 0.850 |
| surface (40 km ring) | point | 7341 | -0.270 | 2.798 | 2.176 |  |
| surface (40 km ring) dressed | dressed | 7341 | -0.270 | 2.798 | 1.564 | 0.861 |
| CNN v0 | point | 7341 | -0.342 | 2.822 | 2.188 |  |
| CNN v0 dressed | dressed | 7341 | -0.342 | 2.822 | 1.572 | 0.854 |
| lookup own cell (not held out) | point | 7341 | -0.355 | 2.783 | 2.173 |  |
| lookup own cell (not held out) dressed | dressed | 7341 | -0.355 | 2.783 | 1.554 | 0.866 |
| CERRA (ceiling) | point | 7341 | -0.135 | 1.262 | 0.882 |  |
| CERRA (ceiling) dressed | dressed | 7341 | -0.135 | 1.262 | 0.783 | 1.909 |

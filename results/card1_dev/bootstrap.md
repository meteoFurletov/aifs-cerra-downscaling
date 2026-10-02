# Score differences per lead

Circular moving-block bootstrap, 2000 replicates, blocks of 5 valid days, stations kept together and resampled (crossed), seed 0; 95 % intervals for A - B on the table's station-times, the replicate spread scaled for the block bootstrap's small-sample bias. With 3 or more temporal folds, where the folds disagree by more than the blocks allow, the excess is added as a between-fold variance and the interval widened; fold share is its part of the day variance (score_stations.bootstrap). Blank: fewer than 20 valid days at that lead. Negative RMSE/CRPS differences favour A.

## Lead +0 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.113 | -0.162 | -0.063 | 8501 | 63 | 3 | 0.546 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.117 | -0.160 | -0.075 | 8501 | 63 | 3 | 0.000 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.068 | -0.104 | -0.031 | 8501 | 63 | 3 | 0.340 |
| CNN v0 dressed | AIFS ENS | me | 0.025 | -0.204 | 0.254 | 8501 | 63 | 3 | 0.797 |
| CNN v0 dressed | AIFS ENS | rmse | -0.011 | -0.115 | 0.093 | 8501 | 63 | 3 | 0.783 |
| CNN v0 dressed | AIFS ENS | crps | -0.008 | -0.106 | 0.090 | 8501 | 63 | 3 | 0.805 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.203 | -0.269 | -0.135 | 8501 | 63 | 3 | 0.695 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.129 | -0.188 | -0.072 | 8501 | 63 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.063 | -0.106 | -0.020 | 8501 | 63 | 3 | 0.297 |
| bilinear dressed | AIFS ENS | me | 0.008 | -0.018 | 0.034 | 8501 | 63 | 3 | 0.404 |
| bilinear dressed | AIFS ENS | rmse | -0.036 | -0.067 | -0.006 | 8501 | 63 | 3 | 0.201 |
| bilinear dressed | AIFS ENS | crps | -0.022 | -0.044 | -0.001 | 8501 | 63 | 3 | 0.371 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.121 | -0.161 | -0.081 | 8501 | 63 | 3 | 0.607 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.081 | -0.125 | -0.040 | 8501 | 63 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.045 | -0.078 | -0.014 | 8501 | 63 | 3 | 0.186 |
| CNN v0 dressed | bilinear dressed | me | 0.017 | -0.200 | 0.234 | 8501 | 63 | 3 | 0.785 |
| CNN v0 dressed | bilinear dressed | rmse | 0.025 | -0.084 | 0.134 | 8501 | 63 | 3 | 0.787 |
| CNN v0 dressed | bilinear dressed | crps | 0.015 | -0.076 | 0.105 | 8501 | 63 | 3 | 0.813 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.211 | -0.267 | -0.153 | 8501 | 63 | 3 | 0.759 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.093 | -0.151 | -0.041 | 8501 | 63 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.041 | -0.078 | -0.005 | 8501 | 63 | 3 | 0.170 |

## Lead +24 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.092 | -0.142 | -0.044 | 8336 | 62 | 3 | 0.289 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.069 | -0.114 | -0.024 | 8336 | 62 | 3 | 0.209 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.043 | -0.073 | -0.013 | 8336 | 62 | 3 | 0.141 |
| CNN v0 dressed | AIFS ENS | me | -0.006 | -0.220 | 0.208 | 8336 | 62 | 3 | 0.784 |
| CNN v0 dressed | AIFS ENS | rmse | 0.023 | -0.048 | 0.094 | 8336 | 62 | 3 | 0.243 |
| CNN v0 dressed | AIFS ENS | crps | 0.019 | -0.018 | 0.055 | 8336 | 62 | 3 | 0.493 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.179 | -0.241 | -0.117 | 8336 | 62 | 3 | 0.567 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.117 | -0.180 | -0.055 | 8336 | 62 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.067 | -0.111 | -0.027 | 8336 | 62 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | me | 0.002 | -0.025 | 0.030 | 8336 | 62 | 3 | 0.381 |
| bilinear dressed | AIFS ENS | rmse | -0.045 | -0.078 | -0.013 | 8336 | 62 | 3 | 0.425 |
| bilinear dressed | AIFS ENS | crps | -0.030 | -0.055 | -0.005 | 8336 | 62 | 3 | 0.490 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.095 | -0.140 | -0.050 | 8336 | 62 | 3 | 0.752 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.024 | -0.064 | 0.015 | 8336 | 62 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.013 | -0.037 | 0.010 | 8336 | 62 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | me | -0.009 | -0.207 | 0.190 | 8336 | 62 | 3 | 0.768 |
| CNN v0 dressed | bilinear dressed | rmse | 0.068 | 0.006 | 0.147 | 8336 | 62 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | crps | 0.049 | 0.016 | 0.084 | 8336 | 62 | 3 | 0.017 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.181 | -0.239 | -0.123 | 8336 | 62 | 3 | 0.703 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.071 | -0.129 | -0.022 | 8336 | 62 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.037 | -0.073 | -0.007 | 8336 | 62 | 3 | 0.000 |

## Lead +48 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.057 | -0.109 | -0.006 | 8170 | 61 | 3 | 0.420 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.066 | -0.110 | -0.022 | 8170 | 61 | 3 | 0.272 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.043 | -0.073 | -0.014 | 8170 | 61 | 3 | 0.261 |
| CNN v0 dressed | AIFS ENS | me | -0.001 | -0.241 | 0.239 | 8170 | 61 | 3 | 0.785 |
| CNN v0 dressed | AIFS ENS | rmse | 0.028 | -0.041 | 0.098 | 8170 | 61 | 3 | 0.270 |
| CNN v0 dressed | AIFS ENS | crps | 0.021 | -0.013 | 0.054 | 8170 | 61 | 3 | 0.349 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.146 | -0.208 | -0.083 | 8170 | 61 | 3 | 0.602 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.116 | -0.176 | -0.056 | 8170 | 61 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.071 | -0.112 | -0.032 | 8170 | 61 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | me | 0.001 | -0.025 | 0.028 | 8170 | 61 | 3 | 0.329 |
| bilinear dressed | AIFS ENS | rmse | -0.041 | -0.070 | -0.012 | 8170 | 61 | 3 | 0.352 |
| bilinear dressed | AIFS ENS | crps | -0.029 | -0.052 | -0.006 | 8170 | 61 | 3 | 0.475 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.058 | -0.106 | -0.010 | 8170 | 61 | 3 | 0.742 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.025 | -0.063 | 0.014 | 8170 | 61 | 3 | 0.061 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.014 | -0.036 | 0.007 | 8170 | 61 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | me | -0.002 | -0.229 | 0.224 | 8170 | 61 | 3 | 0.773 |
| CNN v0 dressed | bilinear dressed | rmse | 0.070 | 0.007 | 0.141 | 8170 | 61 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | crps | 0.050 | 0.018 | 0.083 | 8170 | 61 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.147 | -0.205 | -0.088 | 8170 | 61 | 3 | 0.689 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.075 | -0.130 | -0.030 | 8170 | 61 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.042 | -0.075 | -0.014 | 8170 | 61 | 3 | 0.000 |

## Lead +72 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.048 | -0.103 | 0.007 | 8004 | 60 | 3 | 0.654 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.064 | -0.106 | -0.022 | 8004 | 60 | 3 | 0.133 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.043 | -0.073 | -0.015 | 8004 | 60 | 3 | 0.176 |
| CNN v0 dressed | AIFS ENS | me | 0.001 | -0.272 | 0.274 | 8004 | 60 | 3 | 0.769 |
| CNN v0 dressed | AIFS ENS | rmse | 0.021 | -0.041 | 0.085 | 8004 | 60 | 3 | 0.115 |
| CNN v0 dressed | AIFS ENS | crps | 0.012 | -0.018 | 0.043 | 8004 | 60 | 3 | 0.272 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.139 | -0.207 | -0.070 | 8004 | 60 | 3 | 0.700 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.110 | -0.172 | -0.054 | 8004 | 60 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.070 | -0.112 | -0.033 | 8004 | 60 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | me | 0.000 | -0.026 | 0.027 | 8004 | 60 | 3 | 0.432 |
| bilinear dressed | AIFS ENS | rmse | -0.036 | -0.064 | -0.009 | 8004 | 60 | 3 | 0.251 |
| bilinear dressed | AIFS ENS | crps | -0.026 | -0.046 | -0.006 | 8004 | 60 | 3 | 0.319 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.048 | -0.099 | 0.003 | 8004 | 60 | 3 | 0.777 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.027 | -0.067 | 0.006 | 8004 | 60 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.017 | -0.041 | 0.003 | 8004 | 60 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | me | 0.001 | -0.258 | 0.259 | 8004 | 60 | 3 | 0.753 |
| CNN v0 dressed | bilinear dressed | rmse | 0.057 | -0.002 | 0.127 | 8004 | 60 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | crps | 0.039 | 0.006 | 0.073 | 8004 | 60 | 3 | 0.147 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.139 | -0.205 | -0.073 | 8004 | 60 | 3 | 0.740 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.074 | -0.128 | -0.029 | 8004 | 60 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.043 | -0.079 | -0.016 | 8004 | 60 | 3 | 0.000 |

## Lead +120 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | 0.006 | -0.048 | 0.060 | 7672 | 58 | 3 | 0.638 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.046 | -0.079 | -0.014 | 7672 | 58 | 3 | 0.000 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.032 | -0.052 | -0.011 | 7672 | 58 | 3 | 0.000 |
| CNN v0 dressed | AIFS ENS | me | 0.021 | -0.326 | 0.369 | 7672 | 58 | 3 | 0.741 |
| CNN v0 dressed | AIFS ENS | rmse | 0.006 | -0.076 | 0.089 | 7672 | 58 | 3 | 0.427 |
| CNN v0 dressed | AIFS ENS | crps | 0.000 | -0.040 | 0.041 | 7672 | 58 | 3 | 0.401 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.080 | -0.145 | -0.015 | 7672 | 58 | 3 | 0.657 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.076 | -0.123 | -0.031 | 7672 | 58 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.049 | -0.079 | -0.022 | 7672 | 58 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | me | -0.000 | -0.028 | 0.027 | 7672 | 58 | 3 | 0.629 |
| bilinear dressed | AIFS ENS | rmse | -0.023 | -0.045 | -0.000 | 7672 | 58 | 3 | 0.011 |
| bilinear dressed | AIFS ENS | crps | -0.016 | -0.031 | -0.001 | 7672 | 58 | 3 | 0.198 |
| surface (40 km ring) dressed | bilinear dressed | me | 0.006 | -0.041 | 0.054 | 7672 | 58 | 3 | 0.688 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.024 | -0.056 | 0.005 | 7672 | 58 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.016 | -0.036 | 0.002 | 7672 | 58 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | me | 0.022 | -0.312 | 0.356 | 7672 | 58 | 3 | 0.729 |
| CNN v0 dressed | bilinear dressed | rmse | 0.029 | -0.048 | 0.105 | 7672 | 58 | 3 | 0.305 |
| CNN v0 dressed | bilinear dressed | crps | 0.016 | -0.021 | 0.053 | 7672 | 58 | 3 | 0.203 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.080 | -0.138 | -0.021 | 7672 | 58 | 3 | 0.634 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.053 | -0.097 | -0.016 | 7672 | 58 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.033 | -0.060 | -0.010 | 7672 | 58 | 3 | 0.000 |

## Lead +168 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | 0.156 | 0.089 | 0.223 | 7341 | 56 | 3 | 0.760 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.048 | -0.095 | -0.003 | 7341 | 56 | 3 | 0.000 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.033 | -0.062 | -0.005 | 7341 | 56 | 3 | 0.000 |
| CNN v0 dressed | AIFS ENS | me | 0.084 | -0.303 | 0.470 | 7341 | 56 | 3 | 0.730 |
| CNN v0 dressed | AIFS ENS | rmse | -0.024 | -0.150 | 0.102 | 7341 | 56 | 3 | 0.518 |
| CNN v0 dressed | AIFS ENS | crps | -0.024 | -0.098 | 0.049 | 7341 | 56 | 3 | 0.461 |
| lookup own cell (not held out) dressed | AIFS ENS | me | 0.070 | -0.014 | 0.154 | 7341 | 56 | 3 | 0.746 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.062 | -0.109 | -0.019 | 7341 | 56 | 3 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.043 | -0.074 | -0.014 | 7341 | 56 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | me | 0.002 | -0.024 | 0.029 | 7341 | 56 | 3 | 0.592 |
| bilinear dressed | AIFS ENS | rmse | -0.012 | -0.029 | 0.007 | 7341 | 56 | 3 | 0.000 |
| bilinear dressed | AIFS ENS | crps | -0.008 | -0.019 | 0.003 | 7341 | 56 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | me | 0.154 | 0.096 | 0.211 | 7341 | 56 | 3 | 0.793 |
| surface (40 km ring) dressed | bilinear dressed | rmse | -0.036 | -0.079 | 0.006 | 7341 | 56 | 3 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | -0.025 | -0.053 | 0.003 | 7341 | 56 | 3 | 0.000 |
| CNN v0 dressed | bilinear dressed | me | 0.081 | -0.291 | 0.454 | 7341 | 56 | 3 | 0.719 |
| CNN v0 dressed | bilinear dressed | rmse | -0.012 | -0.134 | 0.111 | 7341 | 56 | 3 | 0.528 |
| CNN v0 dressed | bilinear dressed | crps | -0.016 | -0.087 | 0.055 | 7341 | 56 | 3 | 0.468 |
| lookup own cell (not held out) dressed | bilinear dressed | me | 0.068 | -0.007 | 0.143 | 7341 | 56 | 3 | 0.749 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | -0.050 | -0.092 | -0.012 | 7341 | 56 | 3 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | -0.034 | -0.063 | -0.009 | 7341 | 56 | 3 | 0.000 |

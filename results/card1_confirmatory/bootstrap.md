# Score differences per lead

Circular moving-block bootstrap, 2000 replicates, blocks of 5 valid days, stations kept together and resampled (crossed), seed 0; 95 % intervals for A - B on the table's station-times, the replicate spread scaled for the block bootstrap's small-sample bias. With 3 or more temporal folds, where the folds disagree by more than the blocks allow, the excess is added as a between-fold variance and the interval widened; fold share is its part of the day variance (score_stations.bootstrap). Blank: fewer than 20 valid days at that lead. Negative RMSE/CRPS differences favour A.

## Lead +0 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.109 | -0.152 | -0.067 | 33874 | 210 | 10 | 0.760 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.031 | -0.070 | 0.008 | 33874 | 210 | 10 | 0.494 |
| surface (40 km ring) dressed | AIFS ENS | crps | 0.006 | -0.022 | 0.033 | 33874 | 210 | 10 | 0.564 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.203 | -0.259 | -0.148 | 33874 | 210 | 10 | 0.739 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.025 | -0.076 | 0.026 | 33874 | 210 | 10 | 0.536 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | 0.024 | -0.013 | 0.062 | 33874 | 210 | 10 | 0.611 |
| bilinear dressed | AIFS ENS | me | 0.007 | -0.009 | 0.024 | 33874 | 210 | 10 | 0.726 |
| bilinear dressed | AIFS ENS | rmse | -0.049 | -0.078 | -0.020 | 33874 | 210 | 10 | 0.562 |
| bilinear dressed | AIFS ENS | crps | -0.031 | -0.049 | -0.013 | 33874 | 210 | 10 | 0.594 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.116 | -0.156 | -0.076 | 33874 | 210 | 10 | 0.803 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.018 | -0.008 | 0.044 | 33874 | 210 | 10 | 0.420 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.037 | 0.018 | 0.056 | 33874 | 210 | 10 | 0.514 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.211 | -0.267 | -0.156 | 33874 | 210 | 10 | 0.793 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.024 | -0.012 | 0.060 | 33874 | 210 | 10 | 0.489 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.055 | 0.027 | 0.084 | 33874 | 210 | 10 | 0.584 |

## Lead +24 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.067 | -0.116 | -0.017 | 33874 | 210 | 10 | 0.734 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.033 | -0.067 | 0.001 | 33874 | 210 | 10 | 0.431 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.002 | -0.026 | 0.021 | 33874 | 210 | 10 | 0.552 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.150 | -0.211 | -0.089 | 33874 | 210 | 10 | 0.674 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.032 | -0.083 | 0.019 | 33874 | 210 | 10 | 0.560 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | 0.011 | -0.027 | 0.048 | 33874 | 210 | 10 | 0.638 |
| bilinear dressed | AIFS ENS | me | 0.007 | -0.011 | 0.025 | 33874 | 210 | 10 | 0.721 |
| bilinear dressed | AIFS ENS | rmse | -0.046 | -0.077 | -0.016 | 33874 | 210 | 10 | 0.321 |
| bilinear dressed | AIFS ENS | crps | -0.026 | -0.045 | -0.009 | 33874 | 210 | 10 | 0.363 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.074 | -0.118 | -0.029 | 33874 | 210 | 10 | 0.736 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.014 | -0.009 | 0.036 | 33874 | 210 | 10 | 0.549 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.024 | 0.007 | 0.040 | 33874 | 210 | 10 | 0.591 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.157 | -0.216 | -0.097 | 33874 | 210 | 10 | 0.570 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.014 | -0.023 | 0.051 | 33874 | 210 | 10 | 0.611 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.037 | 0.008 | 0.066 | 33874 | 210 | 10 | 0.663 |

## Lead +48 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.043 | -0.095 | 0.009 | 33874 | 210 | 10 | 0.717 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.025 | -0.056 | 0.005 | 33874 | 210 | 10 | 0.409 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.002 | -0.023 | 0.020 | 33874 | 210 | 10 | 0.539 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.124 | -0.186 | -0.062 | 33874 | 210 | 10 | 0.649 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.025 | -0.071 | 0.021 | 33874 | 210 | 10 | 0.556 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | 0.007 | -0.026 | 0.040 | 33874 | 210 | 10 | 0.628 |
| bilinear dressed | AIFS ENS | me | 0.008 | -0.012 | 0.027 | 33874 | 210 | 10 | 0.713 |
| bilinear dressed | AIFS ENS | rmse | -0.040 | -0.067 | -0.015 | 33874 | 210 | 10 | 0.190 |
| bilinear dressed | AIFS ENS | crps | -0.022 | -0.038 | -0.008 | 33874 | 210 | 10 | 0.269 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.051 | -0.098 | -0.003 | 33874 | 210 | 10 | 0.761 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.014 | -0.007 | 0.036 | 33874 | 210 | 10 | 0.572 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.021 | 0.005 | 0.036 | 33874 | 210 | 10 | 0.598 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.132 | -0.192 | -0.071 | 33874 | 210 | 10 | 0.712 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.015 | -0.020 | 0.050 | 33874 | 210 | 10 | 0.623 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.029 | 0.003 | 0.056 | 33874 | 210 | 10 | 0.660 |

## Lead +72 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | -0.037 | -0.090 | 0.016 | 33874 | 210 | 10 | 0.707 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.022 | -0.049 | 0.005 | 33874 | 210 | 10 | 0.409 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.003 | -0.023 | 0.017 | 33874 | 210 | 10 | 0.515 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.121 | -0.186 | -0.055 | 33874 | 210 | 10 | 0.595 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.021 | -0.064 | 0.023 | 33874 | 210 | 10 | 0.574 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | 0.004 | -0.027 | 0.034 | 33874 | 210 | 10 | 0.613 |
| bilinear dressed | AIFS ENS | me | 0.007 | -0.012 | 0.027 | 33874 | 210 | 10 | 0.718 |
| bilinear dressed | AIFS ENS | rmse | -0.034 | -0.056 | -0.012 | 33874 | 210 | 10 | 0.261 |
| bilinear dressed | AIFS ENS | crps | -0.019 | -0.033 | -0.006 | 33874 | 210 | 10 | 0.379 |
| surface (40 km ring) dressed | bilinear dressed | me | -0.044 | -0.093 | 0.005 | 33874 | 210 | 10 | 0.762 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.012 | -0.008 | 0.032 | 33874 | 210 | 10 | 0.494 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.016 | 0.002 | 0.031 | 33874 | 210 | 10 | 0.516 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.129 | -0.192 | -0.064 | 33874 | 210 | 10 | 0.708 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.013 | -0.021 | 0.046 | 33874 | 210 | 10 | 0.612 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.023 | -0.000 | 0.046 | 33874 | 210 | 10 | 0.627 |

## Lead +120 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | 0.023 | -0.033 | 0.078 | 33874 | 210 | 10 | 0.756 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.013 | -0.034 | 0.008 | 33874 | 210 | 10 | 0.475 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.006 | -0.021 | 0.009 | 33874 | 210 | 10 | 0.519 |
| lookup own cell (not held out) dressed | AIFS ENS | me | -0.062 | -0.129 | 0.006 | 33874 | 210 | 10 | 0.704 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.013 | -0.049 | 0.024 | 33874 | 210 | 10 | 0.614 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.004 | -0.030 | 0.022 | 33874 | 210 | 10 | 0.642 |
| bilinear dressed | AIFS ENS | me | 0.008 | -0.011 | 0.028 | 33874 | 210 | 10 | 0.731 |
| bilinear dressed | AIFS ENS | rmse | -0.024 | -0.039 | -0.010 | 33874 | 210 | 10 | 0.444 |
| bilinear dressed | AIFS ENS | crps | -0.016 | -0.027 | -0.006 | 33874 | 210 | 10 | 0.468 |
| surface (40 km ring) dressed | bilinear dressed | me | 0.015 | -0.038 | 0.067 | 33874 | 210 | 10 | 0.788 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.011 | -0.005 | 0.028 | 33874 | 210 | 10 | 0.468 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.010 | -0.002 | 0.021 | 33874 | 210 | 10 | 0.448 |
| lookup own cell (not held out) dressed | bilinear dressed | me | -0.070 | -0.137 | -0.002 | 33874 | 210 | 10 | 0.762 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.012 | -0.018 | 0.041 | 33874 | 210 | 10 | 0.603 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.012 | -0.009 | 0.032 | 33874 | 210 | 10 | 0.633 |

## Lead +168 h

| A | B | metric | A - B | 2.5 % | 97.5 % | n | days | folds | fold share |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| surface (40 km ring) dressed | AIFS ENS | me | 0.181 | 0.118 | 0.244 | 33874 | 210 | 10 | 0.782 |
| surface (40 km ring) dressed | AIFS ENS | rmse | -0.013 | -0.042 | 0.013 | 33874 | 210 | 10 | 0.000 |
| surface (40 km ring) dressed | AIFS ENS | crps | -0.011 | -0.029 | 0.004 | 33874 | 210 | 10 | 0.000 |
| lookup own cell (not held out) dressed | AIFS ENS | me | 0.100 | 0.022 | 0.178 | 33874 | 210 | 10 | 0.771 |
| lookup own cell (not held out) dressed | AIFS ENS | rmse | -0.013 | -0.041 | 0.014 | 33874 | 210 | 10 | 0.223 |
| lookup own cell (not held out) dressed | AIFS ENS | crps | -0.010 | -0.027 | 0.007 | 33874 | 210 | 10 | 0.181 |
| bilinear dressed | AIFS ENS | me | 0.008 | -0.011 | 0.027 | 33874 | 210 | 10 | 0.741 |
| bilinear dressed | AIFS ENS | rmse | -0.020 | -0.033 | -0.008 | 33874 | 210 | 10 | 0.399 |
| bilinear dressed | AIFS ENS | crps | -0.014 | -0.024 | -0.005 | 33874 | 210 | 10 | 0.494 |
| surface (40 km ring) dressed | bilinear dressed | me | 0.173 | 0.110 | 0.236 | 33874 | 210 | 10 | 0.793 |
| surface (40 km ring) dressed | bilinear dressed | rmse | 0.007 | -0.017 | 0.029 | 33874 | 210 | 10 | 0.000 |
| surface (40 km ring) dressed | bilinear dressed | crps | 0.003 | -0.012 | 0.016 | 33874 | 210 | 10 | 0.000 |
| lookup own cell (not held out) dressed | bilinear dressed | me | 0.092 | 0.013 | 0.171 | 33874 | 210 | 10 | 0.786 |
| lookup own cell (not held out) dressed | bilinear dressed | rmse | 0.007 | -0.014 | 0.028 | 33874 | 210 | 10 | 0.189 |
| lookup own cell (not held out) dressed | bilinear dressed | crps | 0.004 | -0.009 | 0.015 | 33874 | 210 | 10 | 0.015 |

# Station scores per lead

Comparison B: 83 scored SYNOP stations, temporal folds 3 4 5 6 7 8 9 10 11 12, valid 2025-09-18 to 2026-05-30. ME = forecast - obs; a point row's CRPS is its MAE; dressed = N(mean, AIFS spread at the 0.25 deg cell); spread/RMSE = sqrt(mean(s^2)(M+1)/M)/RMSE with s^2 the unbiased member variance (stored spread^2 x M/(M-1)), M = 51.

## Lead +0 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | 0.041 | 1.438 | 0.844 | 0.341 |
| 3 | bilinear | point | 3468 | 0.058 | 1.406 | 0.995 |  |
| 3 | bilinear dressed | dressed | 3468 | 0.058 | 1.406 | 0.823 | 0.349 |
| 3 | surface (40 km ring) | point | 3468 | -0.055 | 1.361 | 0.994 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | -0.055 | 1.361 | 0.819 | 0.361 |
| 3 | lookup own cell (not held out) | point | 3468 | -0.149 | 1.350 | 1.000 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | -0.149 | 1.350 | 0.824 | 0.364 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.522 | 0.526 |
| 4 | AIFS ENS | ensemble | 3290 | -0.083 | 1.111 | 0.614 | 0.404 |
| 4 | bilinear | point | 3290 | -0.067 | 1.069 | 0.735 |  |
| 4 | bilinear dressed | dressed | 3290 | -0.067 | 1.069 | 0.588 | 0.420 |
| 4 | surface (40 km ring) | point | 3290 | -0.176 | 1.111 | 0.807 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | -0.176 | 1.111 | 0.649 | 0.404 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.273 | 1.123 | 0.831 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.273 | 1.123 | 0.672 | 0.400 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.441 | 0.582 |
| 5 | AIFS ENS | ensemble | 3337 | -0.114 | 1.048 | 0.557 | 0.400 |
| 5 | bilinear | point | 3337 | -0.089 | 1.019 | 0.669 |  |
| 5 | bilinear dressed | dressed | 3337 | -0.089 | 1.019 | 0.531 | 0.412 |
| 5 | surface (40 km ring) | point | 3337 | -0.193 | 1.070 | 0.735 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.193 | 1.070 | 0.589 | 0.392 |
| 5 | lookup own cell (not held out) | point | 3337 | -0.300 | 1.094 | 0.764 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -0.300 | 1.094 | 0.615 | 0.384 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.418 | 0.523 |
| 6 | AIFS ENS | ensemble | 3469 | -0.227 | 0.899 | 0.530 | 0.429 |
| 6 | bilinear | point | 3469 | -0.212 | 0.883 | 0.646 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.212 | 0.883 | 0.516 | 0.437 |
| 6 | surface (40 km ring) | point | 3469 | -0.332 | 0.962 | 0.728 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.332 | 0.962 | 0.589 | 0.401 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.433 | 1.022 | 0.789 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.433 | 1.022 | 0.646 | 0.378 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.351 | 0.644 |
| 7 | AIFS ENS | ensemble | 3482 | -0.059 | 1.404 | 0.734 | 0.495 |
| 7 | bilinear | point | 3482 | -0.025 | 1.341 | 0.893 |  |
| 7 | bilinear dressed | dressed | 3482 | -0.025 | 1.341 | 0.691 | 0.518 |
| 7 | surface (40 km ring) | point | 3482 | -0.139 | 1.390 | 0.952 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -0.139 | 1.390 | 0.739 | 0.500 |
| 7 | lookup own cell (not held out) | point | 3482 | -0.236 | 1.405 | 0.972 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -0.236 | 1.405 | 0.757 | 0.495 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 0.515 | 0.710 |
| 8 | AIFS ENS | ensemble | 3098 | 0.032 | 1.797 | 0.995 | 0.476 |
| 8 | bilinear | point | 3098 | 0.054 | 1.755 | 1.207 |  |
| 8 | bilinear dressed | dressed | 3098 | 0.054 | 1.755 | 0.964 | 0.488 |
| 8 | surface (40 km ring) | point | 3098 | -0.046 | 1.762 | 1.233 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | -0.046 | 1.762 | 0.982 | 0.485 |
| 8 | lookup own cell (not held out) | point | 3098 | -0.142 | 1.759 | 1.241 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | -0.142 | 1.759 | 0.987 | 0.486 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 0.779 | 0.608 |
| 9 | AIFS ENS | ensemble | 3447 | -0.285 | 1.513 | 0.837 | 0.414 |
| 9 | bilinear | point | 3447 | -0.286 | 1.487 | 1.020 |  |
| 9 | bilinear dressed | dressed | 3447 | -0.286 | 1.487 | 0.820 | 0.422 |
| 9 | surface (40 km ring) | point | 3447 | -0.425 | 1.524 | 1.089 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -0.425 | 1.524 | 0.877 | 0.411 |
| 9 | lookup own cell (not held out) | point | 3447 | -0.507 | 1.552 | 1.125 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -0.507 | 1.552 | 0.908 | 0.404 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.593 | 0.540 |
| 10 | AIFS ENS | ensemble | 3428 | -0.205 | 1.565 | 0.979 | 0.371 |
| 10 | bilinear | point | 3428 | -0.231 | 1.504 | 1.149 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.231 | 1.504 | 0.941 | 0.386 |
| 10 | surface (40 km ring) | point | 3428 | -0.362 | 1.518 | 1.182 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | -0.362 | 1.518 | 0.969 | 0.382 |
| 10 | lookup own cell (not held out) | point | 3428 | -0.442 | 1.524 | 1.197 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | -0.442 | 1.524 | 0.984 | 0.381 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.605 | 0.543 |
| 11 | AIFS ENS | ensemble | 3420 | -0.143 | 1.712 | 1.036 | 0.337 |
| 11 | bilinear | point | 3420 | -0.155 | 1.629 | 1.191 |  |
| 11 | bilinear dressed | dressed | 3420 | -0.155 | 1.629 | 0.986 | 0.354 |
| 11 | surface (40 km ring) | point | 3420 | -0.272 | 1.615 | 1.204 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | -0.272 | 1.615 | 0.995 | 0.357 |
| 11 | lookup own cell (not held out) | point | 3420 | -0.370 | 1.592 | 1.209 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | -0.370 | 1.592 | 0.997 | 0.362 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.693 | 0.465 |
| 12 | AIFS ENS | ensemble | 3435 | 0.027 | 1.652 | 0.984 | 0.386 |
| 12 | bilinear | point | 3435 | 0.009 | 1.574 | 1.156 |  |
| 12 | bilinear dressed | dressed | 3435 | 0.009 | 1.574 | 0.940 | 0.405 |
| 12 | surface (40 km ring) | point | 3435 | -0.104 | 1.579 | 1.180 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | -0.104 | 1.579 | 0.961 | 0.403 |
| 12 | lookup own cell (not held out) | point | 3435 | -0.195 | 1.561 | 1.179 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | -0.195 | 1.561 | 0.961 | 0.408 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.663 | 0.552 |

## Lead +24 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | -0.095 | 1.579 | 0.847 | 0.572 |
| 3 | bilinear | point | 3468 | -0.076 | 1.516 | 1.088 |  |
| 3 | bilinear dressed | dressed | 3468 | -0.076 | 1.516 | 0.811 | 0.596 |
| 3 | surface (40 km ring) | point | 3468 | -0.149 | 1.490 | 1.093 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | -0.149 | 1.490 | 0.812 | 0.606 |
| 3 | lookup own cell (not held out) | point | 3468 | -0.234 | 1.437 | 1.068 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | -0.234 | 1.437 | 0.790 | 0.628 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.485 | 0.967 |
| 4 | AIFS ENS | ensemble | 3290 | -0.107 | 1.138 | 0.580 | 0.642 |
| 4 | bilinear | point | 3290 | -0.091 | 1.113 | 0.771 |  |
| 4 | bilinear dressed | dressed | 3290 | -0.091 | 1.113 | 0.567 | 0.657 |
| 4 | surface (40 km ring) | point | 3290 | -0.158 | 1.129 | 0.811 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | -0.158 | 1.129 | 0.598 | 0.648 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.245 | 1.136 | 0.842 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.245 | 1.136 | 0.621 | 0.644 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.414 | 0.949 |
| 5 | AIFS ENS | ensemble | 3337 | -0.082 | 1.116 | 0.549 | 0.751 |
| 5 | bilinear | point | 3337 | -0.055 | 1.095 | 0.728 |  |
| 5 | bilinear dressed | dressed | 3337 | -0.055 | 1.095 | 0.530 | 0.765 |
| 5 | surface (40 km ring) | point | 3337 | -0.111 | 1.116 | 0.769 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.111 | 1.116 | 0.560 | 0.751 |
| 5 | lookup own cell (not held out) | point | 3337 | -0.207 | 1.134 | 0.797 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -0.207 | 1.134 | 0.582 | 0.739 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.397 | 1.046 |
| 6 | AIFS ENS | ensemble | 3469 | -0.361 | 1.111 | 0.556 | 0.733 |
| 6 | bilinear | point | 3469 | -0.342 | 1.080 | 0.746 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.342 | 1.080 | 0.540 | 0.755 |
| 6 | surface (40 km ring) | point | 3469 | -0.422 | 1.139 | 0.813 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.422 | 1.139 | 0.593 | 0.715 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.514 | 1.208 | 0.893 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.514 | 1.208 | 0.654 | 0.675 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.345 | 1.359 |
| 7 | AIFS ENS | ensemble | 3482 | -0.182 | 1.932 | 1.007 | 0.677 |
| 7 | bilinear | point | 3482 | -0.147 | 1.882 | 1.342 |  |
| 7 | bilinear dressed | dressed | 3482 | -0.147 | 1.882 | 0.979 | 0.694 |
| 7 | surface (40 km ring) | point | 3482 | -0.224 | 1.932 | 1.396 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -0.224 | 1.932 | 1.021 | 0.677 |
| 7 | lookup own cell (not held out) | point | 3482 | -0.309 | 1.957 | 1.431 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -0.309 | 1.957 | 1.046 | 0.668 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 0.514 | 1.335 |
| 8 | AIFS ENS | ensemble | 3098 | -0.078 | 2.563 | 1.422 | 0.628 |
| 8 | bilinear | point | 3098 | -0.059 | 2.517 | 1.887 |  |
| 8 | bilinear dressed | dressed | 3098 | -0.059 | 2.517 | 1.389 | 0.639 |
| 8 | surface (40 km ring) | point | 3098 | -0.122 | 2.513 | 1.903 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | -0.122 | 2.513 | 1.397 | 0.640 |
| 8 | lookup own cell (not held out) | point | 3098 | -0.216 | 2.515 | 1.911 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | -0.216 | 2.515 | 1.403 | 0.640 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 0.742 | 1.143 |
| 9 | AIFS ENS | ensemble | 3447 | -0.168 | 1.657 | 0.839 | 0.616 |
| 9 | bilinear | point | 3447 | -0.171 | 1.633 | 1.117 |  |
| 9 | bilinear dressed | dressed | 3447 | -0.171 | 1.633 | 0.825 | 0.625 |
| 9 | surface (40 km ring) | point | 3447 | -0.251 | 1.652 | 1.163 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -0.251 | 1.652 | 0.859 | 0.617 |
| 9 | lookup own cell (not held out) | point | 3447 | -0.323 | 1.668 | 1.200 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -0.323 | 1.668 | 0.887 | 0.612 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.559 | 0.878 |
| 10 | AIFS ENS | ensemble | 3428 | -0.110 | 1.592 | 0.903 | 0.615 |
| 10 | bilinear | point | 3428 | -0.135 | 1.542 | 1.175 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.135 | 1.542 | 0.875 | 0.635 |
| 10 | surface (40 km ring) | point | 3428 | -0.214 | 1.554 | 1.199 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | -0.214 | 1.554 | 0.895 | 0.631 |
| 10 | lookup own cell (not held out) | point | 3428 | -0.281 | 1.558 | 1.215 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | -0.281 | 1.558 | 0.907 | 0.629 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.567 | 0.918 |
| 11 | AIFS ENS | ensemble | 3420 | -0.136 | 1.797 | 1.001 | 0.550 |
| 11 | bilinear | point | 3420 | -0.152 | 1.726 | 1.273 |  |
| 11 | bilinear dressed | dressed | 3420 | -0.152 | 1.726 | 0.962 | 0.573 |
| 11 | surface (40 km ring) | point | 3420 | -0.225 | 1.724 | 1.280 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | -0.225 | 1.724 | 0.968 | 0.573 |
| 11 | lookup own cell (not held out) | point | 3420 | -0.309 | 1.682 | 1.254 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | -0.309 | 1.682 | 0.946 | 0.588 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.645 | 0.797 |
| 12 | AIFS ENS | ensemble | 3435 | -0.130 | 1.810 | 1.012 | 0.585 |
| 12 | bilinear | point | 3435 | -0.151 | 1.735 | 1.306 |  |
| 12 | bilinear dressed | dressed | 3435 | -0.151 | 1.735 | 0.975 | 0.610 |
| 12 | surface (40 km ring) | point | 3435 | -0.235 | 1.747 | 1.324 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | -0.235 | 1.747 | 0.989 | 0.606 |
| 12 | lookup own cell (not held out) | point | 3435 | -0.312 | 1.726 | 1.322 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | -0.312 | 1.726 | 0.985 | 0.613 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.621 | 0.917 |

## Lead +48 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | -0.010 | 1.714 | 0.933 | 0.609 |
| 3 | bilinear | point | 3468 | 0.009 | 1.659 | 1.216 |  |
| 3 | bilinear dressed | dressed | 3468 | 0.009 | 1.659 | 0.901 | 0.629 |
| 3 | surface (40 km ring) | point | 3468 | -0.030 | 1.634 | 1.219 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | -0.030 | 1.634 | 0.899 | 0.639 |
| 3 | lookup own cell (not held out) | point | 3468 | -0.112 | 1.574 | 1.179 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | -0.112 | 1.574 | 0.867 | 0.663 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.493 | 1.118 |
| 4 | AIFS ENS | ensemble | 3290 | -0.094 | 1.163 | 0.596 | 0.724 |
| 4 | bilinear | point | 3290 | -0.077 | 1.141 | 0.806 |  |
| 4 | bilinear dressed | dressed | 3290 | -0.077 | 1.141 | 0.584 | 0.738 |
| 4 | surface (40 km ring) | point | 3290 | -0.114 | 1.158 | 0.840 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | -0.114 | 1.158 | 0.611 | 0.727 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.202 | 1.159 | 0.860 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.202 | 1.159 | 0.625 | 0.727 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.417 | 1.093 |
| 5 | AIFS ENS | ensemble | 3337 | -0.174 | 1.260 | 0.627 | 0.867 |
| 5 | bilinear | point | 3337 | -0.143 | 1.233 | 0.842 |  |
| 5 | bilinear dressed | dressed | 3337 | -0.143 | 1.233 | 0.608 | 0.886 |
| 5 | surface (40 km ring) | point | 3337 | -0.183 | 1.255 | 0.885 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.183 | 1.255 | 0.637 | 0.870 |
| 5 | lookup own cell (not held out) | point | 3337 | -0.272 | 1.258 | 0.894 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -0.272 | 1.258 | 0.645 | 0.868 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.414 | 1.363 |
| 6 | AIFS ENS | ensemble | 3469 | -0.371 | 1.269 | 0.627 | 0.831 |
| 6 | bilinear | point | 3469 | -0.352 | 1.243 | 0.851 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.352 | 1.243 | 0.616 | 0.848 |
| 6 | surface (40 km ring) | point | 3469 | -0.403 | 1.294 | 0.910 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.403 | 1.294 | 0.660 | 0.815 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.495 | 1.346 | 0.970 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.495 | 1.346 | 0.705 | 0.783 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.367 | 1.758 |
| 7 | AIFS ENS | ensemble | 3482 | -0.370 | 2.236 | 1.180 | 0.757 |
| 7 | bilinear | point | 3482 | -0.330 | 2.192 | 1.619 |  |
| 7 | bilinear dressed | dressed | 3482 | -0.330 | 2.192 | 1.156 | 0.772 |
| 7 | surface (40 km ring) | point | 3482 | -0.397 | 2.242 | 1.675 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -0.397 | 2.242 | 1.200 | 0.755 |
| 7 | lookup own cell (not held out) | point | 3482 | -0.478 | 2.269 | 1.708 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -0.478 | 2.269 | 1.226 | 0.745 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 0.557 | 1.728 |
| 8 | AIFS ENS | ensemble | 3098 | -0.286 | 2.693 | 1.488 | 0.720 |
| 8 | bilinear | point | 3098 | -0.266 | 2.650 | 2.017 |  |
| 8 | bilinear dressed | dressed | 3098 | -0.266 | 2.650 | 1.459 | 0.732 |
| 8 | surface (40 km ring) | point | 3098 | -0.323 | 2.652 | 2.033 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | -0.323 | 2.652 | 1.467 | 0.732 |
| 8 | lookup own cell (not held out) | point | 3098 | -0.417 | 2.661 | 2.046 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | -0.417 | 2.661 | 1.477 | 0.729 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 0.768 | 1.378 |
| 9 | AIFS ENS | ensemble | 3447 | -0.149 | 1.775 | 0.876 | 0.701 |
| 9 | bilinear | point | 3447 | -0.154 | 1.761 | 1.184 |  |
| 9 | bilinear dressed | dressed | 3447 | -0.154 | 1.761 | 0.866 | 0.707 |
| 9 | surface (40 km ring) | point | 3447 | -0.207 | 1.775 | 1.217 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -0.207 | 1.775 | 0.889 | 0.701 |
| 9 | lookup own cell (not held out) | point | 3447 | -0.276 | 1.796 | 1.251 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -0.276 | 1.796 | 0.915 | 0.693 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.571 | 1.070 |
| 10 | AIFS ENS | ensemble | 3428 | -0.131 | 1.738 | 0.981 | 0.667 |
| 10 | bilinear | point | 3428 | -0.156 | 1.699 | 1.301 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.156 | 1.699 | 0.957 | 0.683 |
| 10 | surface (40 km ring) | point | 3428 | -0.211 | 1.708 | 1.323 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | -0.211 | 1.708 | 0.972 | 0.679 |
| 10 | lookup own cell (not held out) | point | 3428 | -0.273 | 1.717 | 1.344 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | -0.273 | 1.717 | 0.987 | 0.675 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.573 | 1.086 |
| 11 | AIFS ENS | ensemble | 3420 | -0.122 | 1.882 | 1.046 | 0.630 |
| 11 | bilinear | point | 3420 | -0.141 | 1.826 | 1.359 |  |
| 11 | bilinear dressed | dressed | 3420 | -0.141 | 1.826 | 1.016 | 0.650 |
| 11 | surface (40 km ring) | point | 3420 | -0.187 | 1.828 | 1.363 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | -0.187 | 1.828 | 1.021 | 0.649 |
| 11 | lookup own cell (not held out) | point | 3420 | -0.267 | 1.789 | 1.344 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | -0.267 | 1.789 | 1.003 | 0.663 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.649 | 0.956 |
| 12 | AIFS ENS | ensemble | 3435 | -0.206 | 1.991 | 1.104 | 0.679 |
| 12 | bilinear | point | 3435 | -0.225 | 1.930 | 1.455 |  |
| 12 | bilinear dressed | dressed | 3435 | -0.225 | 1.930 | 1.073 | 0.701 |
| 12 | surface (40 km ring) | point | 3435 | -0.286 | 1.939 | 1.472 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | -0.286 | 1.939 | 1.082 | 0.697 |
| 12 | lookup own cell (not held out) | point | 3435 | -0.363 | 1.921 | 1.465 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | -0.363 | 1.921 | 1.078 | 0.704 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.631 | 1.172 |

## Lead +72 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | -0.061 | 1.857 | 1.017 | 0.651 |
| 3 | bilinear | point | 3468 | -0.041 | 1.805 | 1.339 |  |
| 3 | bilinear dressed | dressed | 3468 | -0.041 | 1.805 | 0.986 | 0.670 |
| 3 | surface (40 km ring) | point | 3468 | -0.078 | 1.785 | 1.343 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | -0.078 | 1.785 | 0.986 | 0.678 |
| 3 | lookup own cell (not held out) | point | 3468 | -0.161 | 1.732 | 1.308 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | -0.161 | 1.732 | 0.957 | 0.699 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.504 | 1.296 |
| 4 | AIFS ENS | ensemble | 3290 | -0.007 | 1.260 | 0.646 | 0.772 |
| 4 | bilinear | point | 3290 | 0.009 | 1.243 | 0.888 |  |
| 4 | bilinear dressed | dressed | 3290 | 0.009 | 1.243 | 0.638 | 0.783 |
| 4 | surface (40 km ring) | point | 3290 | -0.015 | 1.257 | 0.919 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | -0.015 | 1.257 | 0.661 | 0.774 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.104 | 1.254 | 0.932 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.104 | 1.254 | 0.671 | 0.776 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.423 | 1.263 |
| 5 | AIFS ENS | ensemble | 3337 | -0.230 | 1.432 | 0.721 | 0.934 |
| 5 | bilinear | point | 3337 | -0.199 | 1.411 | 0.993 |  |
| 5 | bilinear dressed | dressed | 3337 | -0.199 | 1.411 | 0.706 | 0.948 |
| 5 | surface (40 km ring) | point | 3337 | -0.237 | 1.431 | 1.030 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.237 | 1.431 | 0.730 | 0.935 |
| 5 | lookup own cell (not held out) | point | 3337 | -0.330 | 1.443 | 1.038 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -0.330 | 1.443 | 0.740 | 0.927 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.442 | 1.669 |
| 6 | AIFS ENS | ensemble | 3469 | -0.251 | 1.513 | 0.768 | 0.895 |
| 6 | bilinear | point | 3469 | -0.231 | 1.497 | 1.054 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.231 | 1.497 | 0.759 | 0.905 |
| 6 | surface (40 km ring) | point | 3469 | -0.266 | 1.529 | 1.099 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.266 | 1.529 | 0.792 | 0.886 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.358 | 1.564 | 1.142 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.358 | 1.564 | 0.823 | 0.865 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.402 | 2.257 |
| 7 | AIFS ENS | ensemble | 3482 | -0.607 | 2.704 | 1.430 | 0.807 |
| 7 | bilinear | point | 3482 | -0.566 | 2.664 | 1.993 |  |
| 7 | bilinear dressed | dressed | 3482 | -0.566 | 2.664 | 1.408 | 0.819 |
| 7 | surface (40 km ring) | point | 3482 | -0.639 | 2.713 | 2.053 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -0.639 | 2.713 | 1.451 | 0.804 |
| 7 | lookup own cell (not held out) | point | 3482 | -0.728 | 2.742 | 2.092 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -0.728 | 2.742 | 1.479 | 0.796 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 0.628 | 2.228 |
| 8 | AIFS ENS | ensemble | 3098 | -0.191 | 2.902 | 1.582 | 0.810 |
| 8 | bilinear | point | 3098 | -0.172 | 2.873 | 2.200 |  |
| 8 | bilinear dressed | dressed | 3098 | -0.172 | 2.873 | 1.564 | 0.818 |
| 8 | surface (40 km ring) | point | 3098 | -0.219 | 2.875 | 2.207 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | -0.219 | 2.875 | 1.570 | 0.817 |
| 8 | lookup own cell (not held out) | point | 3098 | -0.318 | 2.887 | 2.222 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | -0.318 | 2.887 | 1.581 | 0.814 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 0.814 | 1.670 |
| 9 | AIFS ENS | ensemble | 3447 | -0.380 | 1.997 | 1.008 | 0.845 |
| 9 | bilinear | point | 3447 | -0.387 | 1.984 | 1.399 |  |
| 9 | bilinear dressed | dressed | 3447 | -0.387 | 1.984 | 0.999 | 0.851 |
| 9 | surface (40 km ring) | point | 3447 | -0.449 | 2.000 | 1.428 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -0.449 | 2.000 | 1.019 | 0.844 |
| 9 | lookup own cell (not held out) | point | 3447 | -0.522 | 2.027 | 1.463 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -0.522 | 2.027 | 1.043 | 0.833 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.612 | 1.453 |
| 10 | AIFS ENS | ensemble | 3428 | -0.137 | 1.887 | 1.064 | 0.733 |
| 10 | bilinear | point | 3428 | -0.162 | 1.851 | 1.436 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.162 | 1.851 | 1.042 | 0.747 |
| 10 | surface (40 km ring) | point | 3428 | -0.209 | 1.855 | 1.448 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | -0.209 | 1.855 | 1.052 | 0.746 |
| 10 | lookup own cell (not held out) | point | 3428 | -0.274 | 1.859 | 1.459 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | -0.274 | 1.859 | 1.060 | 0.744 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.589 | 1.296 |
| 11 | AIFS ENS | ensemble | 3420 | -0.053 | 2.027 | 1.125 | 0.729 |
| 11 | bilinear | point | 3420 | -0.072 | 1.977 | 1.503 |  |
| 11 | bilinear dressed | dressed | 3420 | -0.072 | 1.977 | 1.097 | 0.747 |
| 11 | surface (40 km ring) | point | 3420 | -0.104 | 1.977 | 1.505 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | -0.104 | 1.977 | 1.101 | 0.748 |
| 11 | lookup own cell (not held out) | point | 3420 | -0.187 | 1.942 | 1.489 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | -0.187 | 1.942 | 1.083 | 0.761 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.667 | 1.192 |
| 12 | AIFS ENS | ensemble | 3435 | -0.121 | 2.209 | 1.218 | 0.758 |
| 12 | bilinear | point | 3435 | -0.142 | 2.154 | 1.634 |  |
| 12 | bilinear dressed | dressed | 3435 | -0.142 | 2.154 | 1.188 | 0.777 |
| 12 | surface (40 km ring) | point | 3435 | -0.186 | 2.154 | 1.634 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | -0.186 | 2.154 | 1.187 | 0.777 |
| 12 | lookup own cell (not held out) | point | 3435 | -0.267 | 2.127 | 1.624 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | -0.267 | 2.127 | 1.179 | 0.787 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.654 | 1.450 |

## Lead +120 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | 0.074 | 2.204 | 1.216 | 0.818 |
| 3 | bilinear | point | 3468 | 0.092 | 2.157 | 1.659 |  |
| 3 | bilinear dressed | dressed | 3468 | 0.092 | 2.157 | 1.186 | 0.835 |
| 3 | surface (40 km ring) | point | 3468 | 0.134 | 2.150 | 1.666 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | 0.134 | 2.150 | 1.189 | 0.838 |
| 3 | lookup own cell (not held out) | point | 3468 | 0.049 | 2.092 | 1.621 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | 0.049 | 2.092 | 1.155 | 0.862 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.577 | 1.930 |
| 4 | AIFS ENS | ensemble | 3290 | -0.057 | 1.572 | 0.826 | 0.886 |
| 4 | bilinear | point | 3290 | -0.041 | 1.564 | 1.166 |  |
| 4 | bilinear dressed | dressed | 3290 | -0.041 | 1.564 | 0.822 | 0.890 |
| 4 | surface (40 km ring) | point | 3290 | -0.011 | 1.575 | 1.180 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | -0.011 | 1.575 | 0.835 | 0.884 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.096 | 1.579 | 1.200 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.096 | 1.579 | 0.845 | 0.882 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.467 | 1.807 |
| 5 | AIFS ENS | ensemble | 3337 | -0.659 | 2.137 | 1.093 | 0.959 |
| 5 | bilinear | point | 3337 | -0.625 | 2.108 | 1.525 |  |
| 5 | bilinear dressed | dressed | 3337 | -0.625 | 2.108 | 1.076 | 0.972 |
| 5 | surface (40 km ring) | point | 3337 | -0.625 | 2.112 | 1.541 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.625 | 2.112 | 1.087 | 0.970 |
| 5 | lookup own cell (not held out) | point | 3337 | -0.727 | 2.132 | 1.559 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -0.727 | 2.132 | 1.098 | 0.961 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.552 | 2.556 |
| 6 | AIFS ENS | ensemble | 3469 | -0.470 | 2.608 | 1.325 | 0.860 |
| 6 | bilinear | point | 3469 | -0.450 | 2.594 | 1.874 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.450 | 2.594 | 1.318 | 0.865 |
| 6 | surface (40 km ring) | point | 3469 | -0.438 | 2.605 | 1.901 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.438 | 2.605 | 1.336 | 0.861 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.531 | 2.634 | 1.935 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.531 | 2.634 | 1.360 | 0.852 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.535 | 3.741 |
| 7 | AIFS ENS | ensemble | 3482 | -1.028 | 3.444 | 1.915 | 0.942 |
| 7 | bilinear | point | 3482 | -0.986 | 3.415 | 2.688 |  |
| 7 | bilinear dressed | dressed | 3482 | -0.986 | 3.415 | 1.897 | 0.949 |
| 7 | surface (40 km ring) | point | 3482 | -1.033 | 3.465 | 2.738 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -1.033 | 3.465 | 1.933 | 0.936 |
| 7 | lookup own cell (not held out) | point | 3482 | -1.119 | 3.497 | 2.775 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -1.119 | 3.497 | 1.960 | 0.927 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 0.825 | 3.312 |
| 8 | AIFS ENS | ensemble | 3098 | 0.609 | 4.016 | 2.154 | 0.817 |
| 8 | bilinear | point | 3098 | 0.629 | 4.007 | 3.071 |  |
| 8 | bilinear dressed | dressed | 3098 | 0.629 | 4.007 | 2.145 | 0.819 |
| 8 | surface (40 km ring) | point | 3098 | 0.699 | 4.021 | 3.072 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | 0.699 | 4.021 | 2.149 | 0.816 |
| 8 | lookup own cell (not held out) | point | 3098 | 0.603 | 4.017 | 3.076 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | 0.603 | 4.017 | 2.150 | 0.817 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 0.948 | 2.331 |
| 9 | AIFS ENS | ensemble | 3447 | -0.552 | 2.875 | 1.468 | 1.011 |
| 9 | bilinear | point | 3447 | -0.557 | 2.867 | 2.065 |  |
| 9 | bilinear dressed | dressed | 3447 | -0.557 | 2.867 | 1.461 | 1.014 |
| 9 | surface (40 km ring) | point | 3447 | -0.571 | 2.885 | 2.085 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -0.571 | 2.885 | 1.473 | 1.007 |
| 9 | lookup own cell (not held out) | point | 3447 | -0.642 | 2.906 | 2.107 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -0.642 | 2.906 | 1.489 | 1.000 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.786 | 2.500 |
| 10 | AIFS ENS | ensemble | 3428 | -0.160 | 2.324 | 1.321 | 0.824 |
| 10 | bilinear | point | 3428 | -0.185 | 2.294 | 1.813 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.185 | 2.294 | 1.298 | 0.835 |
| 10 | surface (40 km ring) | point | 3428 | -0.168 | 2.290 | 1.813 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | -0.168 | 2.290 | 1.299 | 0.836 |
| 10 | lookup own cell (not held out) | point | 3428 | -0.235 | 2.285 | 1.812 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | -0.235 | 2.285 | 1.297 | 0.838 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.650 | 1.793 |
| 11 | AIFS ENS | ensemble | 3420 | -0.072 | 2.435 | 1.369 | 0.898 |
| 11 | bilinear | point | 3420 | -0.091 | 2.399 | 1.886 |  |
| 11 | bilinear dressed | dressed | 3420 | -0.091 | 2.399 | 1.347 | 0.911 |
| 11 | surface (40 km ring) | point | 3420 | -0.064 | 2.404 | 1.888 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | -0.064 | 2.404 | 1.350 | 0.909 |
| 11 | lookup own cell (not held out) | point | 3420 | -0.143 | 2.375 | 1.871 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | -0.143 | 2.375 | 1.334 | 0.920 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.746 | 1.762 |
| 12 | AIFS ENS | ensemble | 3435 | -0.172 | 2.951 | 1.622 | 0.824 |
| 12 | bilinear | point | 3435 | -0.190 | 2.909 | 2.240 |  |
| 12 | bilinear dressed | dressed | 3435 | -0.190 | 2.909 | 1.597 | 0.836 |
| 12 | surface (40 km ring) | point | 3435 | -0.173 | 2.905 | 2.234 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | -0.173 | 2.905 | 1.593 | 0.837 |
| 12 | lookup own cell (not held out) | point | 3435 | -0.255 | 2.880 | 2.223 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | -0.255 | 2.880 | 1.580 | 0.844 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.752 | 2.107 |

## Lead +168 h

| tfold | forecast | kind | n | ME | RMSE | CRPS | spread/RMSE |
|---:|---|---|---:|---:|---:|---:|---:|
| 3 | AIFS ENS | ensemble | 3468 | 0.177 | 2.854 | 1.583 | 0.763 |
| 3 | bilinear | point | 3468 | 0.194 | 2.829 | 2.160 |  |
| 3 | bilinear dressed | dressed | 3468 | 0.194 | 2.829 | 1.565 | 0.770 |
| 3 | surface (40 km ring) | point | 3468 | 0.414 | 2.845 | 2.160 |  |
| 3 | surface (40 km ring) dressed | dressed | 3468 | 0.414 | 2.845 | 1.574 | 0.766 |
| 3 | lookup own cell (not held out) | point | 3468 | 0.333 | 2.805 | 2.134 |  |
| 3 | lookup own cell (not held out) dressed | dressed | 3468 | 0.333 | 2.805 | 1.551 | 0.777 |
| 3 | CERRA (ceiling) | point | 3468 | -0.232 | 0.934 | 0.667 |  |
| 3 | CERRA (ceiling) dressed | dressed | 3468 | -0.232 | 0.934 | 0.633 | 2.333 |
| 4 | AIFS ENS | ensemble | 3290 | -0.191 | 2.073 | 1.095 | 0.940 |
| 4 | bilinear | point | 3290 | -0.175 | 2.065 | 1.525 |  |
| 4 | bilinear dressed | dressed | 3290 | -0.175 | 2.065 | 1.091 | 0.944 |
| 4 | surface (40 km ring) | point | 3290 | 0.021 | 2.046 | 1.499 |  |
| 4 | surface (40 km ring) dressed | dressed | 3290 | 0.021 | 2.046 | 1.079 | 0.953 |
| 4 | lookup own cell (not held out) | point | 3290 | -0.069 | 2.046 | 1.511 |  |
| 4 | lookup own cell (not held out) dressed | dressed | 3290 | -0.069 | 2.046 | 1.085 | 0.953 |
| 4 | CERRA (ceiling) | point | 3290 | -0.362 | 0.770 | 0.572 |  |
| 4 | CERRA (ceiling) dressed | dressed | 3290 | -0.362 | 0.770 | 0.547 | 2.530 |
| 5 | AIFS ENS | ensemble | 3337 | -1.089 | 2.779 | 1.503 | 1.018 |
| 5 | bilinear | point | 3337 | -1.057 | 2.749 | 2.092 |  |
| 5 | bilinear dressed | dressed | 3337 | -1.057 | 2.749 | 1.488 | 1.029 |
| 5 | surface (40 km ring) | point | 3337 | -0.921 | 2.697 | 2.060 |  |
| 5 | surface (40 km ring) dressed | dressed | 3337 | -0.921 | 2.697 | 1.462 | 1.049 |
| 5 | lookup own cell (not held out) | point | 3337 | -1.018 | 2.714 | 2.079 |  |
| 5 | lookup own cell (not held out) dressed | dressed | 3337 | -1.018 | 2.714 | 1.474 | 1.042 |
| 5 | CERRA (ceiling) | point | 3337 | -0.322 | 0.802 | 0.545 |  |
| 5 | CERRA (ceiling) dressed | dressed | 3337 | -0.322 | 0.802 | 0.706 | 3.529 |
| 6 | AIFS ENS | ensemble | 3469 | -0.483 | 4.342 | 2.233 | 0.795 |
| 6 | bilinear | point | 3469 | -0.464 | 4.333 | 3.219 |  |
| 6 | bilinear dressed | dressed | 3469 | -0.464 | 4.333 | 2.229 | 0.797 |
| 6 | surface (40 km ring) | point | 3469 | -0.292 | 4.328 | 3.214 |  |
| 6 | surface (40 km ring) dressed | dressed | 3469 | -0.292 | 4.328 | 2.232 | 0.798 |
| 6 | lookup own cell (not held out) | point | 3469 | -0.373 | 4.349 | 3.243 |  |
| 6 | lookup own cell (not held out) dressed | dressed | 3469 | -0.373 | 4.349 | 2.253 | 0.794 |
| 6 | CERRA (ceiling) | point | 3469 | -0.323 | 0.600 | 0.463 |  |
| 6 | CERRA (ceiling) dressed | dressed | 3469 | -0.323 | 0.600 | 0.751 | 5.755 |
| 7 | AIFS ENS | ensemble | 3482 | -1.761 | 4.705 | 2.674 | 0.897 |
| 7 | bilinear | point | 3482 | -1.716 | 4.673 | 3.791 |  |
| 7 | bilinear dressed | dressed | 3482 | -1.716 | 4.673 | 2.654 | 0.903 |
| 7 | surface (40 km ring) | point | 3482 | -1.655 | 4.678 | 3.793 |  |
| 7 | surface (40 km ring) dressed | dressed | 3482 | -1.655 | 4.678 | 2.657 | 0.902 |
| 7 | lookup own cell (not held out) | point | 3482 | -1.740 | 4.707 | 3.825 |  |
| 7 | lookup own cell (not held out) dressed | dressed | 3482 | -1.740 | 4.707 | 2.678 | 0.896 |
| 7 | CERRA (ceiling) | point | 3482 | -0.251 | 0.979 | 0.686 |  |
| 7 | CERRA (ceiling) dressed | dressed | 3482 | -0.251 | 0.979 | 1.033 | 4.309 |
| 8 | AIFS ENS | ensemble | 3098 | 0.982 | 4.793 | 2.563 | 0.852 |
| 8 | bilinear | point | 3098 | 0.998 | 4.788 | 3.613 |  |
| 8 | bilinear dressed | dressed | 3098 | 0.998 | 4.788 | 2.556 | 0.853 |
| 8 | surface (40 km ring) | point | 3098 | 1.269 | 4.858 | 3.653 |  |
| 8 | surface (40 km ring) dressed | dressed | 3098 | 1.269 | 4.858 | 2.588 | 0.841 |
| 8 | lookup own cell (not held out) | point | 3098 | 1.173 | 4.847 | 3.638 |  |
| 8 | lookup own cell (not held out) dressed | dressed | 3098 | 1.173 | 4.847 | 2.581 | 0.843 |
| 8 | CERRA (ceiling) | point | 3098 | -0.375 | 1.408 | 0.995 |  |
| 8 | CERRA (ceiling) dressed | dressed | 3098 | -0.375 | 1.408 | 1.086 | 2.902 |
| 9 | AIFS ENS | ensemble | 3447 | -1.528 | 4.109 | 2.203 | 0.962 |
| 9 | bilinear | point | 3447 | -1.530 | 4.104 | 3.110 |  |
| 9 | bilinear dressed | dressed | 3447 | -1.530 | 4.104 | 2.200 | 0.964 |
| 9 | surface (40 km ring) | point | 3447 | -1.459 | 4.087 | 3.089 |  |
| 9 | surface (40 km ring) dressed | dressed | 3447 | -1.459 | 4.087 | 2.187 | 0.968 |
| 9 | lookup own cell (not held out) | point | 3447 | -1.528 | 4.124 | 3.130 |  |
| 9 | lookup own cell (not held out) dressed | dressed | 3447 | -1.528 | 4.124 | 2.216 | 0.959 |
| 9 | CERRA (ceiling) | point | 3447 | -0.363 | 1.162 | 0.758 |  |
| 9 | CERRA (ceiling) dressed | dressed | 3447 | -0.363 | 1.162 | 0.994 | 3.402 |
| 10 | AIFS ENS | ensemble | 3428 | -0.043 | 2.670 | 1.507 | 0.949 |
| 10 | bilinear | point | 3428 | -0.068 | 2.636 | 2.075 |  |
| 10 | bilinear dressed | dressed | 3428 | -0.068 | 2.636 | 1.482 | 0.961 |
| 10 | surface (40 km ring) | point | 3428 | 0.125 | 2.632 | 2.080 |  |
| 10 | surface (40 km ring) dressed | dressed | 3428 | 0.125 | 2.632 | 1.484 | 0.963 |
| 10 | lookup own cell (not held out) | point | 3428 | 0.064 | 2.613 | 2.064 |  |
| 10 | lookup own cell (not held out) dressed | dressed | 3428 | 0.064 | 2.613 | 1.472 | 0.970 |
| 10 | CERRA (ceiling) | point | 3428 | -0.414 | 1.068 | 0.769 |  |
| 10 | CERRA (ceiling) dressed | dressed | 3428 | -0.414 | 1.068 | 0.745 | 2.374 |
| 11 | AIFS ENS | ensemble | 3420 | 0.084 | 3.028 | 1.713 | 0.913 |
| 11 | bilinear | point | 3420 | 0.062 | 3.003 | 2.421 |  |
| 11 | bilinear dressed | dressed | 3420 | 0.062 | 3.003 | 1.698 | 0.921 |
| 11 | surface (40 km ring) | point | 3420 | 0.278 | 3.027 | 2.430 |  |
| 11 | surface (40 km ring) dressed | dressed | 3420 | 0.278 | 3.027 | 1.710 | 0.914 |
| 11 | lookup own cell (not held out) | point | 3420 | 0.195 | 2.997 | 2.419 |  |
| 11 | lookup own cell (not held out) dressed | dressed | 3420 | 0.195 | 2.997 | 1.696 | 0.923 |
| 11 | CERRA (ceiling) | point | 3420 | -0.276 | 1.240 | 0.869 |  |
| 11 | CERRA (ceiling) dressed | dressed | 3420 | -0.276 | 1.240 | 0.830 | 2.231 |
| 12 | AIFS ENS | ensemble | 3435 | 0.179 | 3.354 | 1.871 | 0.862 |
| 12 | bilinear | point | 3435 | 0.162 | 3.311 | 2.580 |  |
| 12 | bilinear dressed | dressed | 3435 | 0.162 | 3.311 | 1.845 | 0.873 |
| 12 | surface (40 km ring) | point | 3435 | 0.371 | 3.339 | 2.599 |  |
| 12 | surface (40 km ring) dressed | dressed | 3435 | 0.371 | 3.339 | 1.861 | 0.866 |
| 12 | lookup own cell (not held out) | point | 3435 | 0.299 | 3.298 | 2.570 |  |
| 12 | lookup own cell (not held out) dressed | dressed | 3435 | 0.299 | 3.298 | 1.838 | 0.876 |
| 12 | CERRA (ceiling) | point | 3435 | -0.241 | 1.154 | 0.849 |  |
| 12 | CERRA (ceiling) dressed | dressed | 3435 | -0.241 | 1.154 | 0.830 | 2.504 |

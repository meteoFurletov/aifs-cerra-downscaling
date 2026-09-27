# Intent: see what WeatherNext 3 can do for 2 m temperature next to AIFS ENS

Author: Nikita Furletov. Owner: Nikita Furletov. Status: split. Date: 2026-09-27.

## Problem

WN3 was released in September 2026 and looks like the state of the art. Unlike AIFS ENS,
its 2 m temperature is already on a ~5 km grid, the scale of CERRA and of our downscaled
output. Nobody on this project has worked with its data, and we do not know how it scores
over Leningrad Oblast against AIFS ENS, CERRA or the SYNOP stations.

## Outcome

WN3 sits alongside AIFS ENS in the project's comparisons: at the stations, against CERRA
and against the downscaled AIFS ENS forecast, as full ensembles, per lead and season. We
know what WN3 is able to do here, its station calibration included.

## Children

1. `002-wn3-data` — WN3 2 m temperature, all members, over the domain for a period chosen from the data's size and archive coverage.
2. `003-aifs-members` — AIFS ENS held as 51 members for the same dates, so both models can be scored as ensembles.
3. `004-wn3-stations` — WN3 and raw AIFS ENS scored at the SYNOP stations, per lead and season.
4. `005-wn3-cerra` — WN3 and AIFS ENS scored against CERRA on the target window, per lead and season.
5. `006-wn3-vs-downscaled` — WN3 against the downscaled AIFS ENS forecast at the stations; waits for a downscaled forecast.

## Out of scope

- The 31 October write-up. This is an exploratory side analysis; its goals are unchanged.
- WN3 as an input to downscaling.

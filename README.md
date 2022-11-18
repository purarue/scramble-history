# scramble-history

Parses your rubiks cube solve history from [cstimer.net](https://cstimer.net/), [cubers.io](https://www.cubers.io/), [twistytimer](https://play.google.com/store/apps/details?id=com.aricneto.twistytimer&hl=en_US&gl=US)

.. and combines/merges solves from those sources into a single format, allowing you to do statistics/giving you uniform averages/a full history

## Installation

Requires `python3.8+`

To install with pip, run:

    pip install scramble_history

To install JSON/graph support: `pip install scramble_history[optional]`

## Input Formats

If theres some other format you'd like to use, feel free to [open an issue](https://github.com/seanbreckenridge/scramble-history/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) (ideally with a data export so I can try to parse it)

### cstimer

To use, export cstimer.net solves to a file, which `scramble_history parse cstimer` accepts as input:

```
$ scramble_history parse cstimer ~/Downloads/cstimer_20221014_231808.txt

Use sess to review session data

In [1]: sess[0].raw_scramble_type
Out[1]: '333'

In [2]: sess[0].solves[-1]
Out[2]: Solve(scramble="D U2 F2 U' F2 R2 D B2 U' L2 F2 U2 B R U F' L U2 L2 F U'", comment='', solve_time=Decimal('25.248'), penalty=Decimal('0'), dnf=False, when=datetime.datetime(2022, 10, 15, 6, 8, 8, tzinfo=datetime.timezone.utc))
```

Or to dump to JSON:

```
$ scramble_history parse cstimer -j ~/data/cubing/cstimer/1665942943939.json | jq '.[].solves | .[0]'
{
  "scramble": "F U' F2 U R2 D L2 F2 U B2 D' L2 D2 R F' U R2 D L2 F' L",
  "comment": "",
  "solve_time": "25.969",
  "penalty": "0",
  "dnf": false,
  "when": "2022-10-11T03:24:27+00:00"
}
```

To backup my <http://cstimer.net> data automatically, I use [cstimer-save-server](https://github.com/seanbreckenridge/cstimer-save-server)

### twistytimer | cubers.io

Parses the export for the [TwistyTimer](https://play.google.com/store/apps/details?id=com.aricneto.twistytimer&hl=en_US&gl=US) android app, which [cubers.io](https://www.cubers.io/) also exports to:

```
$ scramble_history parse twistytimer --json Backup_2022-10-17_20-19.txt | jq '.[0]'
{
  "puzzle": "333",
  "category": "Normal",
  "scramble": "F L2 B' F' D2 R2 D2 F2 L2 U2 F2 R' F' U2 L2 B D L' B U B2",
  "time": "19.86",
  "penalty": "0",
  "dnf": false,
  "when": "2022-10-18T02:00:42.099000+00:00",
  "comment": ""
}
```

Note: for `cubers.io`, the 'when' (datetime when you did the solve) is the same for every solve in a competition (in other words, when the competition began)

## merge

```
Usage: scramble_history merge [OPTIONS] [DATAFILES]

  merge solves from different data sources together

  To provide input, either define a config file, or pass paths like:

  --cstimer ~/Downloads/cstimer.json
  --twistytimer ~/Downloads/*twistytimer*.txt

Options:
  -s, --sourcemap-file FILE       Data file which saves choices on how to map solves from different sources
                                  [default: /home/sean/.config/scramble_history/sourcemap.json]
  -a, --action [json|repl|stats]  what to do with merged solves  [default: repl]
  -C, --check                     Dont print/interact, just check that all solves are transformed properly
  -g, --group-by [puzzle|event_code|event_description]
                                  Group parsed results by key
  -G, --graph                     graph grouped results
  -O, --graph-opt [show|save|date-axis|kitty-print|annotate|annotate-average]
                                  graph options
  -q, --query TEXT                Solves to filter to, or actions to run
  -s, --sort-by [when]            Sort the resulting solves
  -r, --reverse / --no-reverse    Reverse the sort for --sort-by. Default is --no-reverse, stats uses
                                  --reverse
  --help                          Show this message and exit.
```

The merge command lets you combine solves from different sources into a normalized schema. It does this by prompting you to define attributes from each solve to look for, and then converts any solve it finds with those values to the same description. For example:

```json
{
  "source_class_name": "scramble_history.cstimer.Solve",
  "source_fields_match": {
    "name": "3x3",
    "raw_scramble_type": "333"
  },
  "transformed_puzzle": "333",
  "transformed_event_code": "WCA",
  "transformed_event_description": "3x3 CFOP"
}
```

Whenever it finds the same `class`, `name` and `raw_scramble_type` (fields from `cstimer.Solve`), it tags them with the `puzzle`, `event_code` and `event_description`. Those are entered by you (once per new type of solve), and then saved to `~/.config/scramble_history/sourcemap.json`. As an example of the generated file, you can see mine [here](https://sean.fish/d/scramble_history/sourcemap.json?redirect)

The merge command accepts options which describe the filetype, and then multiple files, removing any duplicate solves it finds. E.g.:

```bash
scramble_history merge --action json \
    --cstimer ~/data/cubing/cstimer/*.json \
    --twistytimer ~/data/cubing/phone_twistytimer/* ~/data/cubing/cubers_io/* ~/data/cubing/manual.csv
```

You can also create a config file at `~/.config/scramble_history/files.yaml` (config directory location can be changed with the `SCRAMBLE_HISTORY_CONFIG_DIR` environment variable) which contains similar info, so you don't have to type it out every time:

```yaml
cstimer:
  - ~/data/cubing/cstimer/*.json
twistytimer:
  - ~/data/cubing/manual.csv
  - ~/data/cubing/phone_twistytimer/*.txt
  - ~/data/cubing/cubers_io/*.txt
```

Examples:

```bash
$ scramble_history merge -g event_description -a json
 | jq 'to_entries[] | "\(.value | length) \(.key)"' -r | sort -nr

834 3x3 CFOP
295 2x2
112 3x3 CFOP OH
99 3x3 2-GEN <RU>
95 3x3 LSE
65 4x4
37 3x3 Roux
35 Skewb
25 Pyraminx
20 3x3 F2L
5 3x3 Roux OH
```

It can also calculate running averages across your merged data:

```
[ ~/Repos/scramble-history | master ] $ python3 -m scramble_history merge -a stats
Passed 'stats' with no '--group_by', grouping by 'event_description'
===================
3x3 CFOP
===================
Best => 11.880
Worst => 48.049
Most recent Ao5 => 17.436 = 16.551 17.682 (24.941) (16.531) 18.076
Global Mean (841/847) => 19.681
Solve Count => 847

3x3 CFOP    Current      Best
----------  ---------  ------
Ao5         17.436     14.647
Ao12        18.605     16.898
Ao50        18.725     18.092
Ao100       DNF        18.444
===================
2x2
===================
Best => 3.121
Worst => 50.170
Most recent Ao5 => 6.403 = (7.240) 6.480 6.250 (6.150) 6.480
Global Mean (317/318) => 8.820
Solve Count => 318

2x2      Current    Best
-----  ---------  ------
Ao5        6.403   5.58
Ao12       7.494   6.252
Ao50       7.574   7.214
Ao100      7.553   7.427
===================
4x4
===================
Best => 1:15.592
Worst => 5:39.830
Most recent Ao5 => 1:33.173 = (1:27.770) (1:41.280) 1:38.735 1:28.795 1:31.988
Global Mean (129/129) => 2:25.470
Solve Count => 129

4x4    Current    Best
-----  ---------  --------
Ao5    1:33.173   1:33.173
Ao12   1:36.256   1:36.256
Ao50   1:51.013   1:51.013
Ao100  2:09.471   2:09.471
===================
3x3 CFOP OH
===================
Best => 19.890
Worst => 1:32.280
Most recent Ao5 => 30.640 = 29.760 (26.800) 31.410 (32.450) 30.750
Global Mean (117/117) => 36.919
Solve Count => 117

3x3 CFOP OH      Current    Best
-------------  ---------  ------
Ao5               30.64   26.61
Ao12              29.123  29.123
Ao50              32.776  32.285
Ao100             32.923  32.923
```

Or provide other commands to run instead of `--action stats`:

```
scramble_history merge -q 'event_description==3x3 CFOP' -q Mo3 -q Ao5 -q Ao12
Mo3: 21.413 = 25.969 22.220 16.050
Ao5: 22.037 = (25.969) 22.220 (16.050) 22.697 21.193
Ao12: 19.297 = (25.969) 22.220 (16.050) 22.697 21.193 16.210 16.338 17.824 19.697 21.107 16.538 19.144
```

### graphs

Note: this requires `seaborn`, install with `pip install 'scramble-history[optional]'`

For each group selected by `--group-by`, this creates a graph. By default, this pauses at each group and shows the graph so you can move around/zoom in

To save to a png, use `--graph-opt save`. If you use [kitty](https://sw.kovidgoyal.net/kitty/), can also print these directly in the terminal:

<img src="https://github.com/seanbreckenridge/scramble-history/blob/master/.github/kitty.png?raw=true" height=500>

Can also be used in combination with `--query drop:` and `--query limit:` to only graph a portion of your history. For example to graph a rolling `ao12` from some time ago:

`scramble_history merge -q 'event_description==3x3 CFOP' -q drop:750 -q limit:12 --no-reverse -g event_description -G --graph-opt kitty-print`

<img src="https://github.com/seanbreckenridge/scramble-history/blob/master/.github/ao12.png?raw=true" height=300>

Can provide the `annotate` options if you want to add some of the text onto the graph:

`scramble_history merge -q 'event_description==4x4' -q 'last:5' -G --graph-opt annotate --graph-opt annotate-average`

<img src="https://github.com/seanbreckenridge/scramble-history/blob/master/.github/annotated.png?raw=true" height=300>

### merge query commands:

#### filter

`'attribute_name==attribute_value'` - lets you filter based on any of the string values, e.g.:

```
comment
event_code
event_description
puzzle
scramble
```

Examples:

- `'event_description==3x3 CFOP'`
- `'puzzle==skewb'`
- `'puzzle==222'`

What the description/puzzle names are depend on what you set them as while merging

#### filterin

If you want to match one of many items, e.g. filter just down to `3x3` and `2x2` solves, use `?=`:

```
scramble_history merge -q 'event_description?=["3x3 CFOP", "2x2"]' -a stats
```

Note: The right side of `?=` is JSON

To quickly review my own stats, I have a shell function like:

```bash
cube-stats() {
	scramble_history merge -q 'event_description?=["3x3 CFOP", "3x3 CFOP OH", "2x2", "4x4"]' -a stats -g event_description "$@"
}
```

#### drop/limit

`drop:n` or `limit:n` where `n` is a number. This can be used in between commands to update the current solve list.

Drop removes `n` items at the beginning of the list, limit keeps the first `n` items. For example:

```
scramble_history merge -q 'puzzle==222' -q Ao5 -q 'drop:3' -q Mo2
Ao5: 6.437 = 5.680 7.220 (DNF) 6.410 (5.480)
Mo2: 5.945 = 6.410 5.480
```

```
$ scramble_history merge -q 'event_description==3x3 CFOP' -q 'limit:5' -q dump
19.520
16.040
18.240
21.780
23.980
```

#### dump

Prints the time/description (if DNF) for each solve:

```
$ scramble_history merge -q 'puzzle==222' -q 'limit:5' -q dump
5.680
7.220
DNF
6.410
5.480
```

### best

Prints the best solve from a list of solves:

```
$ scramble_history merge -q 'puzzle==222' -q best
3.121
```

### first/head tail/last

These let you take the first or last `n` items, like `limit`. To get your most recent `Ao5`:

```bash
$ scramble_history merge --no-reverse -q 'event_description==4x4' -q 'last:5' -q ao5
Ao5: 1:44.160 = 1:49.547 1:45.144 1:37.790 (1:52.195) (1:32.934)
```

#### compute averages

`Aon` or `Mon`, where 'n' is a number. Examples: `Ao5`, `Ao500`, `Mo10`

## wca results downloader/extractor

This is a WIP -- it does allow you to download the export and extract your times, but not relate those directly to the scrambles from each group

Downloads the TSV export from <https://www.worldcubeassociation.org/results/misc/export.html> and lets you extract records/scrambles from those rounds from the giant TSV files for your WCA user ID

Also extracts competition/location data for any competitions you've attended

```
$ scramble_history export wca update
[I 221017 23:02:52 wca_export:80] Downloading TSV export...
[I 221017 23:02:58 wca_export:96] Saved TSV export to /home/sean/.cache/wca_export/tsv
$ scramble_history export wca extract -u 2017BREC02
...

$ scramble_history export wca extract -u 2017BREC02 --json | jq '.results_w_scrambles | .[] | .[0] | "\(.competitionId) \(.eventId) \(.value1) \(.value2) \(.value3) \(.value4) \(.value5)"' -r
BerkeleySummer2017 skewb 2009 2326 0 0 0
BerkeleySummer2017 333fm -1 0 0 0 0
BerkeleySummer2017 333 3983 2737 2531 2379 2562
BerkeleySummer2017 222 750 1017 994 791 946
FrozenFingersGhaziabad2018 333oh 3309 3275 3334 3044 3421
BayAreaSpeedcubin132019 444 -1 13954 0 0 0
BayAreaSpeedcubin132019 222 800 599 611 575 784
BayAreaSpeedcubin132019 skewb 1702 2182 794 1404 1495
BayAreaSpeedcubin132019 333 1757 3154 2065 2063 1998
BayAreaSpeedcubin132019 333oh 3988 3233 3416 4600 3839
BayAreaSpeedcubin212019 333 1674 1603 1322 1732 1854
BayAreaSpeedcubin212019 333 2114 1765 1913 1691 2096
BayAreaSpeedcubin212019 444 11331 10607 0 0 0
BayAreaSpeedcubin212019 pyram 1592 1934 -1 2088 1521
BayAreaSpeedcubin212019 skewb 1272 1999 1924 1222 2143
```

## Tests

```bash
git clone 'https://github.com/seanbreckenridge/scramble-history'
cd ./scramble-history
pip install '.[testing]'
pytest
flake8 ./scramble_history
mypy ./scramble_history
```

# scramble-history

parses your rubiks cube scramble history from [cstimer.net](https://cstimer.net/), [cubers.io](https://www.cubers.io/), [twistytimer](https://play.google.com/store/apps/details?id=com.aricneto.twistytimer&hl=en_US&gl=US) and the [WCA TSV export](https://www.worldcubeassociation.org/results/misc/export.html)

## Installation

Requires `python3.8+`

To install with pip, run:

    pip install scramble_history

To install JSON support: `pip install scramble_history[optional]`

## cstimer

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

## twistytimer | cubers.io

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

## merge

```
Usage: scramble_history merge [OPTIONS] [DATAFILES]

  merge solves from different data sources together

Options:
  -s, --sourcemap-file FILE       Data file which saves choices on how to map solves from different sources
                                  [default: /home/sean/.config/scramble_history_sourcemap.json]
  -a, --action [json|repl|stats]  what to do with merged solves  [default: repl]
  -C, --check                     Dont print/interact, just check that all solves are transformed properly
  -g, --group-by [puzzle|event_code|event_description]
                                  Group parsed results by key
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

Whenever it finds the same `class`, `name` and `raw_scramble_type` (fields from `cstimer.Solve`), it tags them with the `puzzle`, `event_code` and `event_description`. Those are entered by you (once per new type of solve), and then saved to `~/.config/scramble_history_sourcemap.json`. As an example of the generated file, you can see mine [here](https://sean.fish/d/scramble_history_sourcemap.json?redirect)

The merge command accepts options which describe the filetype, and then multiple files, removing any duplicate solves it finds. E.g.:

```bash
python3 -m scramble_history merge --action json \
    --cstimer ~/data/cubing/cstimer/*.json \
    --twistytimer ~/data/cubing/phone_twistytimer/* ~/data/cubing/cubers_io/* ~/data/cubing/manual.csv
```

You can also create a config file at `~/.config/scramble_history.yaml` (location can be changed with the `SCRAMBLE_HISTORY_CONFIG` environment variable) which contains similar info, so you don't have to type it out every time:

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
$ python3 -m scramble_history merge -g event_description -a json
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
$ python3 -m scramble_history merge -a stats
==============
2x2
==============
Most recent Ao5 => 6.437 = 5.680 7.220 (DNF) 6.410 (5.480)
Ao5: 6.437
Ao12: 8.215
Ao50: 7.381
Ao100: 7.582
==============
3x3 CFOP
==============
Most recent Ao5 => 19.847 = 19.520 (16.040) 18.240 21.780 (23.980)
Ao5: 19.847
Ao12: 19.115
Ao50: 18.603
Ao100: DNF
==============
3x3 CFOP OH
==============
Most recent Ao5 => 29.327 = 29.800 (34.950) 27.750 (26.710) 30.430
Ao5: 29.327
Ao12: 29.879
Ao50: 32.892
Ao100: 33.766
==============
4x4
==============
Most recent Ao5 => 2:41.123 = 2:53.280 (3:31.680) (2:14.690) 2:50.200 2:19.890
Ao5: 2:41.123
Ao12: 2:38.749
Ao50: 2:47.116
Ao100: --
```

## wca results downloader/extractor

This is a WIP -- it does allow you to download the export and extract your times, but not relate those directly to the scrambles from each group

Downloads the TSV export from <https://www.worldcubeassociation.org/results/misc/export.html> and lets you extract records/scrambles from those rounds from the giant TSV files for your WCA user ID

Also extracts competition/location data for any competitions you've attended

```
$ scramble_history export wca update
[I 221017 23:02:52 wca_export:80] Downloading TSV export...
[I 221017 23:02:58 wca_export:96] Saved TSV export to /home/sean/.cache/wca_export/tsv
$ python3 -m scramble_history export wca extract -u 2017BREC02
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

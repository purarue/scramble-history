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
$ scramble_history parse cstimer -j cstimer.json | jq '.[] | select(.raw_scramble_type == "333") | .solves | .[] | "\(.when) \(.solve_time) \(.scramble)"' -r | head
2022-10-11T03:24:27+00:00 25.969 F U' F2 U R2 D L2 F2 U B2 D' L2 D2 R F' U R2 D L2 F' L
2022-10-11T03:25:16+00:00 22.22 R' U' F2 D2 U' F2 L2 U2 F2 U' L B' R' D2 F L' D F L
2022-10-11T03:26:01+00:00 16.05 D' B' L F U2 F2 U' R2 B U2 D L2 D B2 U' L2 U' F2 L2
2022-10-11T03:26:43+00:00 22.697 F B U F2 R' L2 U2 B U D2 B' L2 B' D2 R2 B2 U2 D2 B L2 B
2022-10-11T03:27:27+00:00 21.193 R2 F B2 L2 U2 R2 D B2 L2 D B2 D' R2 U2 R F' L' B' D2 L2 D'
2022-10-11T03:28:07+00:00 16.21 L' D U2 B D2 R2 B D2 U2 B F2 L2 F' D' L' D L D R2 U'
2022-10-11T03:28:45+00:00 16.338 L' U' R D2 U2 F2 L' F2 L2 F2 D2 R2 F2 R' F' D' L2 B' D F' L'
2022-10-11T03:30:11+00:00 17.824 B' R F2 U' L' F2 R2 L' B' F2 R2 F2 U L2 U' D2 F2 D2 R2
2022-10-11T03:30:49+00:00 19.697 B2 D' L U2 B' L2 B' L2 F U2 B R B D' F2 R2 D R
2022-10-11T03:31:30+00:00 21.107 B' U2 R2 F2 R2 B2 U' B2 F2 D2 L D' F R2 B' D' F R' U2
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

## wca results downloader/extractor

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

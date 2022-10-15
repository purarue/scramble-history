# scramble-history

WIP

parses scramble history from cstimer.net and other sources

TODO:

- parse scramble codes into names/enum
- allow dumping parsed data to JSON
- integrate with <https://github.com/seanbreckenridge/cube-scramble-cli>

## Installation

Requires `python3.7+`

To install with pip, run:

    pip install scramble_history

## Usage

To use, export cstimer.net solves to a file, which `scramble_history parse cstimer` accepts as input:

```
$ scramble_history parse cstimer ~/Downloads/cstimer_20221014_231808.txt

Use sess to review session data

In [1]: sess[0].raw_scramble_type
Out[1]: '333'

In [2]: sess[0].solves[-1]
Out[2]: Solve(scramble="D U2 F2 U' F2 R2 D B2 U' L2 F2 U2 B R U F' L U2 L2 F U'", comment='', solve_time=Decimal('25.248'), penalty=Decimal('0'), dnf=False, when=datetime.datetime(2022, 10, 15, 6, 8, 8, tzinfo=datetime.timezone.utc))
```

### Tests

```bash
git clone 'https://github.com/seanbreckenridge/scramble-history'
cd ./scramble-history
pip install '.[testing]'
pytest
flake8 ./scramble_history
mypy ./scramble_history
```

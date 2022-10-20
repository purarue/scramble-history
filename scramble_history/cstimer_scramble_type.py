from typing import NamedTuple, Optional
from functools import lru_cache


class CSTimerScramble(NamedTuple):
    scramble_code: str
    category: Optional[str]
    name: Optional[str]


# instead of dict/mapping just save all possible data
# there is some overlap between what the 'correct' description
# to return for a scramble is depending on which category the user
# had selected, so not going to try to be optimal here
SCRAMBLES = [
    CSTimerScramble(scramble_code="333", category=None, name="3x3x3"),
    CSTimerScramble(scramble_code="222so", category=None, name="2x2x2"),
    CSTimerScramble(scramble_code="444wca", category=None, name="4x4x4"),
    CSTimerScramble(scramble_code="555wca", category=None, name="5x5x5"),
    CSTimerScramble(scramble_code="666wca", category=None, name="6x6x6"),
    CSTimerScramble(scramble_code="777wca", category=None, name="7x7x7"),
    CSTimerScramble(scramble_code="333ni", category=None, name="3x3 bld"),
    CSTimerScramble(scramble_code="333fm", category=None, name="3x3 fm"),
    CSTimerScramble(scramble_code="333oh", category=None, name="3x3 oh"),
    CSTimerScramble(scramble_code="clkwca", category=None, name="clock"),
    CSTimerScramble(scramble_code="mgmp", category=None, name="megaminx"),
    CSTimerScramble(scramble_code="pyrso", category=None, name="pyraminx"),
    CSTimerScramble(scramble_code="skbso", category=None, name="skewb"),
    CSTimerScramble(scramble_code="sqrs", category=None, name="sq1"),
    CSTimerScramble(scramble_code="444bld", category=None, name="4x4 bld"),
    CSTimerScramble(scramble_code="555bld", category=None, name="5x5 bld"),
    CSTimerScramble(scramble_code="r3ni", category=None, name="3x3 mbld"),
    CSTimerScramble(scramble_code="input", category=None, name="Extern"),
    CSTimerScramble(scramble_code="remoteComp", category=None, name="Competition"),
    CSTimerScramble(scramble_code="remoteOther", category=None, name="Remote"),
    CSTimerScramble(scramble_code="333", category="wca", name="random state (WCA)"),
    CSTimerScramble(scramble_code="333o", category="wca", name="random move"),
    CSTimerScramble(scramble_code="333noob", category="wca", name="3x3x3 for noobs"),
    CSTimerScramble(scramble_code="edges", category="wca", name="edges only"),
    CSTimerScramble(scramble_code="corners", category="wca", name="corners only"),
    CSTimerScramble(scramble_code="ll", category="wca", name="last layer"),
    CSTimerScramble(scramble_code="zbll", category="wca", name="zb last layer"),
    CSTimerScramble(scramble_code="cll", category="wca", name="corners of last layer"),
    CSTimerScramble(scramble_code="ell", category="wca", name="edges of last layer"),
    CSTimerScramble(scramble_code="lse", category="wca", name="last six edges"),
    CSTimerScramble(
        scramble_code="lsemu", category="wca", name="last six edges&ltM,U&gt"
    ),
    CSTimerScramble(scramble_code="cmll", category="wca", name="Roux L10P"),
    CSTimerScramble(scramble_code="f2l", category="wca", name="cross solved"),
    CSTimerScramble(
        scramble_code="lsll2", category="wca", name="last slot + last layer"
    ),
    CSTimerScramble(scramble_code="2gll", category="wca", name="2GLL"),
    CSTimerScramble(scramble_code="zbls", category="wca", name="ZBLS"),
    CSTimerScramble(scramble_code="zzll", category="wca", name="ZZLL"),
    CSTimerScramble(scramble_code="oll", category="wca", name="OLL"),
    CSTimerScramble(scramble_code="pll", category="wca", name="PLL"),
    CSTimerScramble(scramble_code="eoline", category="wca", name="EOLine"),
    CSTimerScramble(scramble_code="easyc", category="wca", name="easy cross"),
    CSTimerScramble(scramble_code="333ft", category="wca", name="3x3 ft"),
    CSTimerScramble(scramble_code="222so", category="wca", name="random state (WCA)"),
    CSTimerScramble(scramble_code="222o", category="wca", name="optimal"),
    CSTimerScramble(scramble_code="2223", category="wca", name="3-gen"),
    CSTimerScramble(scramble_code="222eg", category="wca", name="EG"),
    CSTimerScramble(scramble_code="222eg0", category="wca", name="EG0"),
    CSTimerScramble(scramble_code="222eg1", category="wca", name="EG1"),
    CSTimerScramble(scramble_code="222eg2", category="wca", name="EG2"),
    CSTimerScramble(scramble_code="222nb", category="wca", name="No Bar"),
    CSTimerScramble(scramble_code="444wca", category="wca", name="WCA"),
    CSTimerScramble(scramble_code="444m", category="wca", name="random move"),
    CSTimerScramble(scramble_code="444", category="wca", name="SiGN"),
    CSTimerScramble(scramble_code="444yj", category="wca", name="YJ"),
    CSTimerScramble(scramble_code="4edge", category="wca", name="4x4x4 edges"),
    CSTimerScramble(scramble_code="RrUu", category="wca", name="R,r,U,u"),
    CSTimerScramble(scramble_code="555wca", category="wca", name="WCA"),
    CSTimerScramble(scramble_code="555", category="wca", name="SiGN"),
    CSTimerScramble(scramble_code="5edge", category="wca", name="5x5x5 edges"),
    CSTimerScramble(scramble_code="666wca", category="wca", name="WCA"),
    CSTimerScramble(scramble_code="666si", category="wca", name="SiGN"),
    CSTimerScramble(scramble_code="666p", category="wca", name="prefix"),
    CSTimerScramble(scramble_code="666s", category="wca", name="suffix"),
    CSTimerScramble(scramble_code="6edge", category="wca", name="6x6x6 edges"),
    CSTimerScramble(scramble_code="777wca", category="wca", name="WCA"),
    CSTimerScramble(scramble_code="777si", category="wca", name="SiGN"),
    CSTimerScramble(scramble_code="777p", category="wca", name="prefix"),
    CSTimerScramble(scramble_code="777s", category="wca", name="suffix"),
    CSTimerScramble(scramble_code="7edge", category="wca", name="7x7x7 edges"),
    CSTimerScramble(scramble_code="clk", category="wca", name="jaap"),
    CSTimerScramble(scramble_code="clkwca", category="wca", name="wca"),
    CSTimerScramble(scramble_code="clko", category="wca", name="optimal"),
    CSTimerScramble(scramble_code="clkc", category="wca", name="concise"),
    CSTimerScramble(scramble_code="clke", category="wca", name="efficient pin order"),
    CSTimerScramble(scramble_code="mgmp", category="wca", name="WCA"),
    CSTimerScramble(scramble_code="mgmc", category="wca", name="Carrot"),
    CSTimerScramble(scramble_code="mgmo", category="wca", name="old style"),
    CSTimerScramble(scramble_code="pyrso", category="wca", name="random state (WCA)"),
    CSTimerScramble(scramble_code="pyro", category="wca", name="optimal"),
    CSTimerScramble(scramble_code="pyrm", category="wca", name="random move"),
    CSTimerScramble(scramble_code="pyrl4e", category="wca", name="L4E"),
    CSTimerScramble(scramble_code="pyr4c", category="wca", name="4 tips"),
    CSTimerScramble(scramble_code="pyrnb", category="wca", name="No bar"),
    CSTimerScramble(scramble_code="skbso", category="wca", name="random state (WCA)"),
    CSTimerScramble(scramble_code="skbo", category="wca", name="optimal"),
    CSTimerScramble(scramble_code="skb", category="wca", name="random move"),
    CSTimerScramble(scramble_code="skbnb", category="wca", name="No bar"),
    CSTimerScramble(scramble_code="sqrs", category="wca", name="random state (WCA)"),
    CSTimerScramble(scramble_code="sqrcsp", category="wca", name="CSP"),
    CSTimerScramble(scramble_code="sq1h", category="wca", name="face turn metric"),
    CSTimerScramble(scramble_code="sq1t", category="wca", name="twist metric"),
    CSTimerScramble(scramble_code="15prp", category="other", name="random state URLD"),
    CSTimerScramble(scramble_code="15prap", category="other", name="random state ^<>v"),
    CSTimerScramble(
        scramble_code="15prmp", category="other", name="random state Blank"
    ),
    CSTimerScramble(scramble_code="15p", category="other", name="random move URLD"),
    CSTimerScramble(scramble_code="15pat", category="other", name="random move ^<>v"),
    CSTimerScramble(scramble_code="15pm", category="other", name="random move Blank"),
    CSTimerScramble(scramble_code="8prp", category="other", name="random state URLD"),
    CSTimerScramble(scramble_code="8prap", category="other", name="random state ^<>v"),
    CSTimerScramble(scramble_code="8prmp", category="other", name="random state Blank"),
    CSTimerScramble(scramble_code="133", category="other", name="1x3x3 (Floppy Cube)"),
    CSTimerScramble(scramble_code="223", category="other", name="2x2x3 (Tower Cube)"),
    CSTimerScramble(scramble_code="233", category="other", name="2x3x3 (Domino)"),
    CSTimerScramble(scramble_code="334", category="other", name="3x3x4"),
    CSTimerScramble(scramble_code="335", category="other", name="3x3x5"),
    CSTimerScramble(scramble_code="336", category="other", name="3x3x6"),
    CSTimerScramble(scramble_code="337", category="other", name="3x3x7"),
    CSTimerScramble(scramble_code="888", category="other", name="8x8x8"),
    CSTimerScramble(scramble_code="999", category="other", name="9x9x9"),
    CSTimerScramble(scramble_code="101010", category="other", name="10x10x10"),
    CSTimerScramble(scramble_code="111111", category="other", name="11x11x11"),
    CSTimerScramble(scramble_code="cubennn", category="other", name="NxNxN"),
    CSTimerScramble(scramble_code="gearso", category="other", name="random state"),
    CSTimerScramble(scramble_code="gearo", category="other", name="optimal"),
    CSTimerScramble(scramble_code="gear", category="other", name="random move"),
    CSTimerScramble(scramble_code="cm3", category="other", name=None),
    CSTimerScramble(scramble_code="cm2", category="other", name=None),
    CSTimerScramble(scramble_code="giga", category="other", name="Pochmann"),
    CSTimerScramble(scramble_code="heli", category="other", name=None),
    CSTimerScramble(scramble_code="redim", category="other", name="MoYu"),
    CSTimerScramble(scramble_code="redi", category="other", name="old"),
    CSTimerScramble(scramble_code="ivyso", category="other", name="random state"),
    CSTimerScramble(scramble_code="ivyo", category="other", name="optimal"),
    CSTimerScramble(scramble_code="ivy", category="other", name="random move"),
    CSTimerScramble(scramble_code="mpyr", category="other", name=None),
    CSTimerScramble(scramble_code="prcp", category="other", name="Pochmann"),
    CSTimerScramble(scramble_code="prco", category="other", name="old style"),
    CSTimerScramble(scramble_code="sia113", category="other", name="1x1x3 block"),
    CSTimerScramble(scramble_code="sia123", category="other", name="1x2x3 block"),
    CSTimerScramble(scramble_code="sia222", category="other", name="2x2x2 block"),
    CSTimerScramble(scramble_code="sq2", category="other", name=None),
    CSTimerScramble(scramble_code="sfl", category="other", name=None),
    CSTimerScramble(scramble_code="ssq1t", category="other", name="twist metric"),
    CSTimerScramble(scramble_code="ufo", category="other", name="Jaap style"),
    CSTimerScramble(
        scramble_code="fto", category="other", name="FTO (Face-Turning Octahedron)"
    ),
    CSTimerScramble(scramble_code="2gen", category="special", name="2-generator R,U"),
    CSTimerScramble(scramble_code="2genl", category="special", name="2-generator L,U"),
    CSTimerScramble(
        scramble_code="roux", category="special", name="Roux-generator M,U"
    ),
    CSTimerScramble(
        scramble_code="3gen_F", category="special", name="3-generator F,R,U"
    ),
    CSTimerScramble(
        scramble_code="3gen_L", category="special", name="3-generator R,U,L"
    ),
    CSTimerScramble(scramble_code="RrU", category="special", name="3-generator R,r,U"),
    CSTimerScramble(scramble_code="half", category="special", name="half turns only"),
    CSTimerScramble(
        scramble_code="lsll", category="special", name="last slot + last layer (old)"
    ),
    CSTimerScramble(scramble_code="bic", category="special", name="Bicube"),
    CSTimerScramble(scramble_code="bsq", category="special", name="Square-1 /,(1,0)"),
    CSTimerScramble(scramble_code="minx2g", category="special", name="2-generator R,U"),
    CSTimerScramble(
        scramble_code="mlsll", category="special", name="last slot + last layer"
    ),
    CSTimerScramble(scramble_code="r3", category="special", name="lots of 3x3x3s"),
    CSTimerScramble(scramble_code="r234", category="special", name="234 relay"),
    CSTimerScramble(scramble_code="r2345", category="special", name="2345 relay"),
    CSTimerScramble(scramble_code="r23456", category="special", name="23456 relay"),
    CSTimerScramble(scramble_code="r234567", category="special", name="234567 relay"),
    CSTimerScramble(scramble_code="r234w", category="special", name="234 relay (WCA)"),
    CSTimerScramble(
        scramble_code="r2345w", category="special", name="2345 relay (WCA)"
    ),
    CSTimerScramble(
        scramble_code="r23456w", category="special", name="23456 relay (WCA)"
    ),
    CSTimerScramble(
        scramble_code="r234567w", category="special", name="234567 relay (WCA)"
    ),
    CSTimerScramble(scramble_code="111", category="jokes", name="x y z"),
    CSTimerScramble(scramble_code="-1", category="jokes", name=None),
    CSTimerScramble(scramble_code="112", category="jokes", name=None),
    CSTimerScramble(scramble_code="lol", category="jokes", name=None),
    CSTimerScramble(scramble_code="eide", category="jokes", name=None),
]


@lru_cache(maxsize=None)
def parse_scramble_type(code: str) -> CSTimerScramble:
    for scr in SCRAMBLES:
        if code == scr.scramble_code:
            return scr
    raise KeyError(f"Could not find matching scramble code {code}")

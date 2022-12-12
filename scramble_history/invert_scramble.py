def invert_scramble(scramble: str) -> str:
    res = []
    for token in scramble.split():
        if token.endswith("'"):
            res.append(token.strip("'"))
        else:
            res.append(token + "'")
    res.reverse()
    return " ".join(res)

from scramble_history.average_parser import parse_operation_code


def test_twistytimer_serializer() -> None:
    assert parse_operation_code("ao5") == ("average", 5)
    assert parse_operation_code("ao12") == ("average", 12)

    assert parse_operation_code("mo3") == ("mean", 3)
    assert parse_operation_code("mo5") == ("mean", 5)

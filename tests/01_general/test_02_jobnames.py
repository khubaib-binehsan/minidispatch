from minidispatch.db.jobnames import generate_name


def test_generate_name_has_expected_shape() -> None:
    name = generate_name()

    assert "_" in name
    left, right = name.split("_", maxsplit=1)

    assert left
    assert right

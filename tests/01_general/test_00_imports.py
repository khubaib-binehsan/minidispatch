def test_can_import_package() -> None:
    import minidispatch

    assert minidispatch.hello() == "Hello from minidispatch!"

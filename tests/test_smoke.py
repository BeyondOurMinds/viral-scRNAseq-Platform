def test_cli_imports():
    # Basic smoke test to ensure the CLI entry point imports cleanly.
    from viral_platform.gui import ViralApp

    assert ViralApp is not None
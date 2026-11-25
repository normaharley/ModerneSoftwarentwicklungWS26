import pytest

from modernesoftwarentwicklungws26 import main


def test_main_prints_greeting(capsys: pytest.CaptureFixture[str]) -> None:
    main()
    assert capsys.readouterr().out == "Hello from modernesoftwarentwicklungws26!\n"

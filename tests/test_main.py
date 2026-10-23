from modernesoftwarentwicklungws26 import main


def test_main_prints_greeting(capsys):
    main()
    assert capsys.readouterr().out == "Hello from modernesoftwarentwicklungws26!\n"

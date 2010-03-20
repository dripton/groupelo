import groupelo

def test_win_expectancy():
    assert groupelo.win_expectancy(1500, 1500) == 0.5
    assert groupelo.win_expectancy(1501, 1499) > 0.5
    assert groupelo.win_expectancy(1550, 1450) > 0.6
    assert groupelo.win_expectancy(1600, 1400) > 0.7
    assert groupelo.win_expectancy(1700, 1300) > 0.9
    assert groupelo.win_expectancy(2000, 1000) > 0.99

    assert groupelo.win_expectancy(1499, 1501) < 0.5
    assert groupelo.win_expectancy(1450, 1550) < 0.4
    assert groupelo.win_expectancy(1400, 1600) < 0.3
    assert groupelo.win_expectancy(1300, 1700) < 0.1
    assert groupelo.win_expectancy(1000, 2000) < 0.01

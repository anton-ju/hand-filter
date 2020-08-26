from typing import List

import sat16ev
from pathlib import Path
import re


def test_rename_tournament():

    test = "PokerStars Hand #212786566608: Tournament #2881341230, $7.36+$0.14 USD Hold'em No Limit - Match Round II, Level I (25/50) - 2020/04/27 0:00:02 MSK [2020/04/26 17:00:02 ET]"
    expected = "PokerStars Hand #212786566608: Tournament #102881341230, $7.36+$0.14 USD Hold'em No Limit - Match Round II, Level I (25/50) - 2020/04/27 0:00:02 MSK [2020/04/26 17:00:02 ET]"

    result = sat16ev.rename_tournament(test, '10')
    assert result == expected


def test_change_bi():
    test = "PokerStars Hand #212786566608: Tournament #2881341230, $7.36+$0.14 USD Hold'em No Limit - Match Round II, Level I (25/50) - 2020/04/27 0:00:02 MSK [2020/04/26 17:00:02 ET]"
    expected = "PokerStars Hand #212786566608: Tournament #2881341230, $29.44+$0.0 USD Hold'em No Limit - Match Round II, Level I (25/50) - 2020/04/27 0:00:02 MSK [2020/04/26 17:00:02 ET]"
    result = sat16ev.change_bi(test)
    assert result == expected


def test_get_hero():
    test = Path('cases/round1finished1-no-entry.txt').read_text(encoding='utf-8')
    result = sat16ev.get_hero(test)
    expected = "DiggErr555"
    assert expected == result


def test_fix_finishes_round1():
    test: str = Path('cases/round1finished5.txt').read_text(encoding='utf-8')
    result: str = sat16ev.fix_finishes_round1(test)

    assert all(map(lambda x: result.find(x) == -1, ('in 9th', 'in 7th', 'in 5th')))
    assert all(map(lambda x: result.find(x) > -1, ('in 4th', 'in 3rd', 'in 2nd')))


def test_add_round1_winner():
    test = Path('cases/round1finished1.txt').read_text(encoding='utf-8')
    result = sat16ev.add_round1_winner(test)
    expected = "DiggErr555 finished the tournament in 1st place and received $58.84."
    assert expected in result


def test_add_round1_winner_no_hu_in_hh():
    test = Path('cases/round1finished16.txt').read_text(encoding='utf-8')
    result = sat16ev.add_round1_winner(test)
    expected = "finished the tournament in 1st place and received $58.84."
    assert expected in result


def test_add_round1_winner_no_finished_entry():
    test = Path('cases/round1finished1-no-entry.txt').read_text(encoding='utf-8')
    result = sat16ev.add_round1_winner(test)
    expected = "DiggErr555 finished the tournament in 1st place and received $29.44."
    assert expected in result


def test_fix_finishes_round2():
    test: str = Path('cases/round2finished1.txt').read_text(encoding='utf-8')
    result: str = sat16ev.fix_finishes_round2(test)
    expected = "DiggErr555 finished the tournament in 1st place and received $109."
    assert expected in result


def test_fix_finishes_round2_win_entry():
    test: str = Path('cases/round2finished1-win-entry.txt').read_text(encoding='utf-8')
    result: str = sat16ev.fix_finishes_round2(test)
    expected = "DiggErr555 finished the tournament in 1st place and received $55."
    assert expected in result


def test_fix_finishes_round2_no_finishes():
    test: str = Path('cases/round2-no-finishes.txt').read_text(encoding='utf-8')
    result: str = sat16ev.fix_finishes_round2(test)
    expected = "DiggErr555 finished the tournament in 1st place and received $215."
    assert expected in result


def test_remove_win_entry_round2():
    test: str = Path('cases/round2finished1.txt').read_text(encoding='utf-8')
    result: str = sat16ev.remove_win_entry_round2(test)
    not_expected = ["Gselweckle wins an entry to tournament #2869142162",
                    "DiggErr555 wins an entry to tournament #2869142162"]
    assert all(map(lambda x: result.find(x) == -1, not_expected))


def test_get_tournament_id():
    test: str = Path('cases/round2finished1.txt').read_text(encoding='utf-8')
    result: str = sat16ev.get_tournament_id(test)
    expected = "2881133193"
    assert result == expected


def test_split_sat_hh_no_round1_in_file():
    test: str = Path('cases/round2finished1-2.txt').read_text(encoding='utf-8')
    round1, round2 = sat16ev.split_sat_hh(test)
    expected = ""
    assert round1.strip() == expected
    assert round2.strip() == test.strip()


def test_split_sat_hh_no_round2_in_file():
    test: str = Path('cases/round1finished16.txt').read_text(encoding='utf-8')
    round1, round2 = sat16ev.split_sat_hh(test)
    expected = ""
    assert round2 == expected
    assert round1 == test.strip()


def test_get_round1_winner_no_hu():
    test: str = Path('cases/round1finished16.txt').read_text(encoding='utf-8')
    winner, remain_players = sat16ev.get_round1_winner(test)
    expected_winner: str = ""
    expected_players: List[str] = ["kindose", "aaeschaa", "bbtondo"]
    assert winner == expected_winner
    assert sorted(remain_players) == sorted(expected_players)


def test_get_round1_winner_lose_hu():
    test: str = Path('cases/round1finished5.txt').read_text(encoding='utf-8')
    winner = sat16ev.get_round1_winner(test)
    expected = ("gAAoChAAo", ["gAAoChAAo"])
    assert winner == expected


def test_get_round1_winner_win_hu():
    test: str = Path('cases/round1finished1.txt').read_text(encoding='utf-8')
    winner = sat16ev.get_round1_winner(test)
    expected = ("DiggErr555", ["DiggErr555"])
    assert winner == expected


def test_get_round1_winner_1player_not_finished():
    test: str = Path('cases/round1-1player-not-finished.txt').read_text(encoding='utf-8')
    winner = sat16ev.get_round1_winner(test)
    expected = ("anime22", ["anime22"])
    assert winner == expected


def test_get_round1_winner_1player_not_finished_before_hu():
    test: str = Path('cases/round1-1player-not-finished-before-hu.txt').read_text(encoding='utf-8')
    winner = sat16ev.get_round1_winner(test)
    expected = ("pzpm", ["pzpm"])
    assert winner == expected

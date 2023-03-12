import filters
from pypokertools.parsers import PSHandHistory
from utils import load_ps_notes
from pathlib import Path
from filters import HandFilter, Condition
import operator
import datetime

config = {
    "HERO": 'DiggErr555',
    "FISH_LABELS": ('15', '16', '17', '18', 'uu'),
    "REG_LABELS": ('11'),
    "NOTES": 'notes.DiggErr555.xml',
    "INPUT": 'input',
    "OUTPUT": 'output',
    "BIINS": (3.0, 10.0, 25.0, 5.0, 100.0, 50.0),
}
notes = load_ps_notes(config['NOTES'])


def test_bb_reg_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BBRegFilter()
    result = f(parsed, notes=notes, config=config)
    expected = False
    assert result == expected


def test_sb_reg_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.SBRegFilter()
    result = f(parsed, notes=notes, config=config)
    expected = True
    assert result == expected


def test_bu_reg_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BURegFilter()
    result = f(parsed, notes=notes, config=config)
    expected = False
    assert result == expected


def test_co_reg_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.CORegFilter()
    result = f(parsed, notes=notes, config=config)
    expected = False
    assert result == expected


def test_bb_fish_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BBFishFilter()
    result = f(parsed, notes=notes, config=config)
    expected = True
    assert result == expected


def test_sb_fish_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.SBFishFilter()
    result = f(parsed, notes=notes, config=config)
    expected = False
    assert result == expected


def test_bu_fish_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BUFishFilter()
    result = f(parsed, notes=notes, config=config)
    expected = True
    assert result == expected


def test_co_fish_filter():
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.COFishFilter()
    result = f(parsed, **{'notes': notes, 'config': config})
    expected = True
    assert result == expected


def test_bu_covers_sb_bb():
    th = Path('cases/pko/ps-44-pko-8p.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BUCoversSBBB()
    result = f(parsed, **{'notes': notes, 'config': config})
    expected = True
    assert result == expected


def test_bu_not_covers_sb_bb():
    th = Path('cases/pko/ps-44-pko-7p-aipreflop.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f = filters.BUCoversSBBB()
    result = f(parsed, **{'notes': notes, 'config': config})
    expected = False
    assert result == expected


def test_hand_filter_match_3conditions():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f1 = filters.SBRegFilter()
    f2 = filters.BBFishFilter()
    f3 = filters.BUFishFilter()
    hf.add_condition(f1, notes=notes, config=config)
    hf.add_condition(f2, notes=notes, config=config)
    hf.add_condition(f3, notes=notes, config=config)
    result = hf.check_conditions(parsed)
    expected = True
    assert result == expected


def test_hand_filter_not_match():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    f1 = filters.SBFishFilter()
    f2 = filters.BBFishFilter()
    f3 = filters.BUFishFilter()
    hf.add_condition(f1, notes=notes, config=config)
    hf.add_condition(f2, notes=notes, config=config)
    hf.add_condition(f3, notes=notes, config=config)
    result = hf.check_conditions(parsed)
    expected = False
    assert result == expected

def test_condition_bi():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    cond = Condition('bi', operator.gt, 14)
    hf.add_condition(cond, notes=notes, config=config)
    result = hf.check_conditions(parsed)
    expected = True
    assert result == expected


def test_wrong_condition_bi():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    cond = Condition('xxbi', operator.gt, 14)
    hf.add_condition(cond, notes=notes, config=config)
    result = hf.check_conditions(parsed)
    expected = False
    assert result == expected


def test_multi_condition_bi():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    cond1 = Condition('bi', operator.gt, 14)
    cond2 = Condition('hero', operator.eq, "DiggErr555")
    cond3 = Condition('bi', operator.lt, 26)
    hf.add_condition(cond1, notes=notes, config=config)
    hf.add_condition(cond2, notes=notes, config=config)
    hf.add_condition(cond3, notes=notes, config=config)
    result = hf.check_conditions(parsed)
    expected = True
    assert result == expected


def test_condition_dt():
    hf = HandFilter()
    th = Path('cases/bb-not-reg.txt').read_text(encoding='utf-8')
    parsed = PSHandHistory(th)
    dt1 = datetime.datetime(2020, 4, 26, 13, 43)
    dt2 = datetime.datetime(2020, 4, 26, 13, 49)
    cond1 = Condition('datetime', operator.gt, dt1)
    cond2 = Condition('datetime', operator.lt, dt2)
    hf.add_condition(cond1)
    hf.add_condition(cond2)
    result = hf.check_conditions(parsed)
    expected = True
    assert result == expected



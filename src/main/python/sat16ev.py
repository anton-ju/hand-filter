from typing import Tuple, List
from pathlib import Path
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage

import re
import logging
from optparse import OptionParser
import pprint
import json

CWD = Path.cwd()
DEFAULT_INPIT_DIR = 'input'
printer = pprint.PrettyPrinter()
DEFAULT_OUTPUT_DIR = 'output'
ROUND1_DIR = 'round1'
ROUND2_DIR = 'round2'
CONFIG_FILE = 'sat16ev.cfg'

TID_REGEX = "Tournament #(?P<tid>\d+)"
BI_BOUNTY_RAKE_REGEX = TID_REGEX + ",\s\$(?P<bi>\d+?\.\d+)(?:\+\$)?(?P<bounty>\d+?\.\d+)?\+\$(?P<rake>\d+?\.\d+)"
FINISHED = ['4th', '3rd', '2nd', '1st']
FINISHES_REGEX = "(?P<player>.*?) (?:finished.*in (?P<place>\d+)(?:nd|rd|th)|wins the tournament)"
FINISHED_DICT = {1: '1st', 2: '2nd', 3: '3rd', 4: '4th'}
HERO_REGEX = r"Dealt to (?P<hero>.*)\s\["
WINNER_REGEX = "(?P<winner>.*?) wins the tournament"
PRIZE_WON_REGEX = "(?P<player>.*) (?:wins|finished).*and (?:received|receives) \$(?P<prize>\d+\.\d+)(?:.|\s)"

config = {
    "HERO": 'DiggErr555',
    "FISH_LABELS": ('15', '16', '17', '18', 'uu'),
    "REG_LABELS": ('11'),
    "NOTES": 'notes.DiggErr555.xml',
    "INPUT": 'input',
    "OUTPUT": 'output',
    "BIINS": (3.0, 10.0, 25.0, 5.0, 100.0, 50.0),
    "ROUND1_PREFIX": '10',
    "ROUND2_PREFIX": '20',
    'ROUND1_DIR': 'round1',
    'ROUND2_DIR': 'round2'
}

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S')
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.addHandler(ch)


def load_config(config_current, config_file):
    try:
        with open(config_file, 'r') as f:
            config_json = f.read()
            if config_json == '':
                return
            new_config = json.loads(config_json, encoding='utf-8')
            if new_config:
                config_current.update(new_config)
    except IOError:
        logging.error('Error opening config file')
    except json.JSONDecodeError:
        logging.error('Invalid config file structure')


def get_hands_list_from_hh(hh: str) -> List[str]:
    res = []
    hh = hh.split('\n\n')
    for ss in hh:
        if ss == '\n\n' or ss is None or ss == '':
            continue
        res.append(ss)
    return res


def split_sat_hh(hh: str) -> Tuple[str, str]:
    index: int
    linestart: int
    round1: str
    round2: str

    index = hh.find('Match Round I')
    if index == -1:
        return ("", "")
    index = hh.find('Match Round II')
    if index == -1:
        round1 = hh[:]
        round2 = ''
    else:
        line_start = hh.rfind('PokerStars', 0, index)
        round1 = hh[:line_start]
        round2 = hh[line_start:]

    return (round1.strip(), round2.strip())


def get_tournament_id(hh: str) -> str:
    return re.search(TID_REGEX, hh).group(1)


def rename_tournament(hh: str, prefix: str) -> str:
    """ add prefix to tournament number
    """
    return re.sub("Tournament #(?P<tid>\d+)", 'Tournament #' + prefix + '\g<tid>', hh)


def get_round1_winner(hh: str) -> str:
    """ get players from last hand in hh
    """
    regex = "Seat\s?[0-9]:\s(.*)\s\(\s?\$?(\d*,?\d*)\s(?:in\schips)?"
    hands = get_hands_list_from_hh(hh)
    try:
        hand = hands[-1]
    except IndexError:
        return ("", [""])

    players = set(x[0] for x in re.findall(regex, hand))
    finishes = set(x[0] for x in re.findall(FINISHES_REGEX, hand))
    winner = list(players - finishes)
    if len(winner) == 1:
        return (winner[0], winner)
    else:
        return ("", winner)


def paste_finished(hh: str, player: str, place: int, win_bi: float) -> str:
    """ paste string with finishes and awards into history
    """
    matches = list(re.finditer('\*\*\* SUMMARY', hh))
    paste_index = matches[-1].start()
    place_ = FINISHED_DICT.get(place, '1st')
    paste_str = f"{player} finished the tournament in {place_} place and received ${win_bi}.\n"
    res = hh[:paste_index] + paste_str + hh[paste_index:]
    return res


def get_bi(hh: str) -> float:
    regex = ",\s\$(?P<bi>\d+?\.\d+)(?:\+\$)?(?P<bounty>\d+?\.\d+)?\+\$(?P<rake>\d+?\.\d+)"
    re_se = re.search(regex, hh)
    if re_se:
        res = float(re_se.group(1))
    else:
        logger.debug("Hand history:")
        logger.debug(hh)
        # raise RuntimeError
    return res


def get_prize_won(hh: str) -> str:
    re_se = re.search(PRIZE_WON_REGEX, hh)
    res = ''
    if re_se:
        res = re_se.group(1)
    return res


def get_tournament_winner(hh: str) -> str:
    re_se = re.search(WINNER_REGEX, hh)
    res = ''
    if re_se:
        res = re_se.group(1)
    return res


def get_hero(hh: str) -> str:
    re_se = re.search(HERO_REGEX, hh)
    res = ''
    if re_se:
        res = re_se.group(1)

    return res


def add_round1_winner(hh: str) -> str:
    """ paste string into round1 history
        if where are no winner, no hu, we will add random players finishes to let pt4 know what the payouts are
    """
    res = hh
    winner, remain_players = get_round1_winner(hh)
    bi = get_bi(hh)
    if winner:
        res = paste_finished(hh, winner, 1, bi * 4)
    else:
        # there are cases then no message in hh about winning in HU
        # if hero not finished tornament -> he wins HU
        hero = get_hero(hh)
        if hero in remain_players:
            res = paste_finished(hh, hero, 1, bi * 4)
        else:
            for player in remain_players[:1]:
                res = paste_finished(hh, player, 1, bi * 4)
    return res


def fix_finishes_round1(hh: str) -> str:
    replace_list = ['4th', '3rd', '2nd', '1st']
    it = 0
    res = hh
    for m in re.finditer("in (?P<place>\d+)(?:nd|rd|th)", hh):
        res = re.sub(m.group(0), f"in {replace_list[it]}", res)
        it += 1
    return res


def fix_finishes_round2(hh: str) -> str:
    bi_dict = {'14.71': 109,
               '5.59': 44,
               '26.96': 215,
               '7.36': 55,
               '2.85': 22,
               '2.16': 16.5,
               '66.66': 530}
    res = hh
    matches = list(re.finditer('in (?:1st|2nd) place', hh))[::-1]
    bi = re.findall(BI_BOUNTY_RAKE_REGEX, hh)[0][1]
    prize = bi_dict.get(bi, 0)
    place_3 = round(float(bi) * 16 - 2 * prize, 2)
    for m in matches:
        paste_index = m.end()
        paste_str = f' and received ${prize}.'
        res = res[:paste_index] + paste_str + res[paste_index:]
    else:
        # if there are no finishes add random winners to let pt4 know what the payouts are

        prize_won = get_prize_won(hh)
        if not prize_won:
            winner, remain_players = get_round1_winner(hh)
            if len(remain_players) == 3:
                res = paste_finished(res, remain_players[0], 3, place_3)
                res = paste_finished(res, remain_players[1], 1, prize)
                res = paste_finished(res, remain_players[2], 1, prize)

    winner = get_tournament_winner(res)
    " in 3 way all in case "
    if winner:
        res = paste_finished(res, winner, 1, prize)
    return res


def remove_win_entry_round2(hh: str) -> str:
    """ removes win entry string from hh
    """
    res = hh
    matches = list(re.finditer("^.* wins an entry to tournament #\d+\n", hh, re.M))[::-1]
    for m in matches:
        res = res[:m.start()] + res[m.end():]
    return res


def change_bi(hh: str) -> str:
    """ change bi in hh multiplay by 4
    """
    bi = re.findall(BI_BOUNTY_RAKE_REGEX, hh)[0][1]
    return re.sub(BI_BOUNTY_RAKE_REGEX, "Tournament #\g<tid>, $" + str(float(bi)*4) + "+$0.0", hh)


def fix_summaries(hh: str) -> str:
    pass


def open_hh(fn: str):
    p = Path(fn)
    return p.read_text(encoding='utf-8')


# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def get_output_dir(path):
    output_dir_path = CWD.joinpath(path)
    if not output_dir_path.exists():
        output_dir_path.mkdir()
    return output_dir_path


def process_hands(options):

    input_path = CWD.joinpath(options.input_dir)
    if not input_path.exists():
        logging.info('Place hand history files in "input" directory')
        return
    output_dir_path = get_output_dir(options.output_dir)

    round1_path = output_dir_path.joinpath(ROUND1_DIR)
    if not round1_path.exists():
        round1_path.mkdir()
    round2_path = output_dir_path.joinpath(ROUND2_DIR)
    if not round2_path.exists():
        round2_path.mkdir()

    file_list = list(input_path.glob('**/*.txt'))
    total = len(file_list)
    counter = 0
    skipped = 0
    round1_path = output_dir_path.joinpath(ROUND1_DIR).joinpath(str(counter))
    round2_path = output_dir_path.joinpath(ROUND2_DIR).joinpath(str(counter))
    round1_path.mkdir()
    round2_path.mkdir()

    printProgressBar(counter, total)
    for file in file_list:
        s = file.read_text(encoding='utf-8')
        tid = get_tournament_id(s)
        round1, round2 = split_sat_hh(s)
        if not round1 and not round2:
            skipped += 1
            counter += 1
            continue

        prefix = config['ROUND1_PREFIX']
        if round1:
            round1 = add_round1_winner(fix_finishes_round1(rename_tournament(round1, prefix)))

            round1_path.joinpath(prefix + file.name).write_text(round1, encoding='utf-8')

        if round2:
            prefix = config['ROUND2_PREFIX']
            round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, prefix))))
            round2 = round2.replace("Round II", "Round I")
            round2_path.joinpath(prefix + file.name).write_text(round2, encoding='utf-8')

        counter += 1
        if counter % 500 == 0:
            printProgressBar(counter, total)
            round1_path = output_dir_path.joinpath(ROUND1_DIR).joinpath(str(counter))
            round2_path = output_dir_path.joinpath(ROUND2_DIR).joinpath(str(counter))
            round1_path.mkdir()
            round2_path.mkdir()

    logging.info(f'Finished: {counter}, skipped: {skipped}')


def main() -> None:
    # hh = Path('cases/finished1.txt').read_text(encoding='utf-8')
    # tid = get_tournament_id(hh)
    # round1, round2 = split_sat_hh(hh)
    # round1 = add_round1_winner(fix_finishes_round1(rename_tournament(round1, '10')))
    # Path('results/' + '10' + tid + '.txt').write_text(round1, encoding='utf-8')

    # round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, '20'))))

    # Path('results/' + '20' + tid + '.txt').write_text(round2, encoding='utf-8')

    load_config(config, CONFIG_FILE)
    filters = []
    usage = "usage: %prog [options] arg1 arg2"
    op = OptionParser(usage=usage)
    op.add_option("-i", "--input",
                  action="store",
                  default=config["INPUT"],
                  dest="input_dir",
                  help="input directory "
                  " [default: %default]")
    op.add_option("-o", "--output",
                  action="store",
                  default=config["OUTPUT"],
                  dest="output_dir",
                  help="output directory "
                  " [default: %default]")
    (options, args) = op.parse_args()
    process_hands(options)


if __name__ == '__main__':
    main()

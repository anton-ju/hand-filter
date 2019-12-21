"""parse hand history files and save to output dir according to tournament position"""
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
import logging
from optparse import OptionParser
import pprint
from pathlib import Path
from xml.dom import minidom
import json
import re

CWD = Path.cwd()
DEFAULT_INPIT_DIR = 'input'
printer = pprint.PrettyPrinter()
DEFAULT_OUTPUT_DIR = 'output'
ROUND1_DIR = 'round1'
ROUND2_DIR = 'round2'
CONFIG_FILE = 'hand-proc.cfg'

notes = None

config = {
    "HERO": 'DiggErr555',
    "FISH_LABELS": ('15', '16', '17', '18', 'uu'),
    "REG_LABELS": ('11'),
    "NOTES": 'notes.DiggErr555.xml',
    "INPUT": 'input',
    "OUTPUT": 'output',
    "BIINS": (3.0, 10.0, 25.0, 5.0, 100.0, 50.0),
}

FILTERS = {
    "BU_REG": 'bu_reg_filter',
    "SB_REG": 'sb_reg_filter',
    "BB_REG": 'bb_reg_filter',
}


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


def load_ps_notes(notes_file):
    """
    load pokerstars player notes from xml file
    returns: dict {player: note}
    """

    notes_path = Path(notes_file)
    logging.info(notes_path)
    if not notes_path.exists():
        raise RuntimeError('Invalid path to notes file')

    xml = minidom.parse(notes_file)
    notes = xml.getElementsByTagName('note')
    notes_dict = {}
    for note in notes:
        notes_dict[note.attributes['player'].value] = note.attributes['label'].value

    return notes_dict


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


def get_output_dir(path):
    output_dir_path = CWD.joinpath(path)
    if not output_dir_path.exists():
        output_dir_path.mkdir()
    return output_dir_path


def bu_reg_filter(hh):
    for player, pos in hh.positions().items():
        if pos == 'BU' and notes.get(player, 'uu') in config['REG_LABELS']:
            return True
    return False


def sb_reg_filter(hh):
    for player, pos in hh.positions().items():
        if pos == 'SB' and notes.get(player, 'uu') in config['REG_LABELS']:
            return True
    return False


def bb_reg_filter(hh):
    for player, pos in hh.positions().items():
        if pos == 'BB' and notes.get(player, 'uu') in config['REG_LABELS']:
            return True
    return False


def pass_filters(hh, options):
    """
    check if hand pass filters
    returns: boolean
    """
    passed = []
    if options.bu_reg:
        passed.append(bu_reg_filter(hh))
    if options.sb_reg:
        passed.append(sb_reg_filter(hh))
    if options.bb_reg:
        passed.append(bb_reg_filter(hh))

    return all(passed)


def sort_by_tournament_position(options):
    # this script filters hh of sats with 4 playrs tables, suits for 4max and for 3max
    try:
        storage = HandStorage(options.input_dir)
    except IOError:
        logging.exception('Invalid input dir')
        try:
            storage = HandStorage(CWD.joinpath(DEFAULT_INPIT_DIR))
        except IOError:
            logging.exception('Default input dir doesnt exists')
            return

    output_dir_path = get_output_dir(options.output_dir)

    result = []
    pos_codes = set()
    total = len(list(storage.read_hand()))
    counter = 0
    logging.info('Sorting hands...')
    printProgressBar(counter, total)
    for txt in storage.read_hand():
        try:
            hh = PSHandHistory(txt)
        except Exception as e:
            logging.exception("%s " % e)
            continue

        counter += 1
        printProgressBar(counter, total)
        if not pass_filters(hh, options):
            continue

        positions = hh.positions()
        player_pos = {pos: hh.tournamentPosition(player) for player, pos in positions.items()}
        # for now only for 4 and 3 max
        if hh.players_number() == 4:
            pos_str = str(player_pos['CO']) + str(player_pos['BU']) + str(player_pos['SB']) + str(player_pos['BB'])
        elif hh.players_number() == 3:
            pos_str = str(player_pos['BU']) + str(player_pos['SB']) + str(player_pos['BB'])
        else:
            continue
        # for ex. "1234" if CO has 1 stack BU 2 stack SB -3 BB -4
        pos_codes.add(pos_str)
        result_row = {'pos_code': pos_str, 'txt': txt, 'fn': hh.hid}
        result.append(result_row)
    # create all possible output directories from pos_codes
    for pos_code in pos_codes:
        pos_code_dir_path = output_dir_path.joinpath(pos_code)
        if not pos_code_dir_path.exists():
            pos_code_dir_path.mkdir()

    counter = 0
    total = len(result)
    logging.info('Saving results...')
    printProgressBar(counter, total)
    for row in result:
        res_dir_path = output_dir_path.joinpath(row['pos_code'])
        res_file_path = res_dir_path.joinpath(row['fn']).with_suffix('.txt')
        res_file_path.write_text(row['txt'], encoding='utf-8')
        counter += 1
        printProgressBar(counter, total)


def renumber_places(hh_text):
    pattern = re.compile('finished the tournament in (.+)th\splace')
    pass


def split(options):
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
        index = s.find('Match Round I')
        if index == -1:
            skipped += 1
            continue
        index = s.find('Match Round II')
        if index == -1:
            round1 = s[:]
            round2 = ''
            round1_path.joinpath(file.name).write_text(round1, encoding='utf-8')
        else:
            line_start = s.rfind('PokerStars', 0, index)
            round1 = s[:line_start]
            round2 = s[line_start:]
            round1_path.joinpath(file.name).write_text(round1, encoding='utf-8')
            round2_path.joinpath(file.name).write_text(round2, encoding='utf-8')
        counter += 1
        if counter % 500 == 0:
            printProgressBar(counter, total)
            round1_path = output_dir_path.joinpath(ROUND1_DIR).joinpath(str(counter))
            round2_path = output_dir_path.joinpath(ROUND2_DIR).joinpath(str(counter))
            round1_path.mkdir()
            round2_path.mkdir()

    logging.info(f'Finished: {counter}, skipped: {skipped}')


def add_filter(option, opt_str, value, parser):
    option.values.filters.append(opt_str[2:])


def main():
    load_config(config, CONFIG_FILE)
    filters = []
    usage = "usage: %prog [options] arg1 arg2"
    op = OptionParser(usage=usage)
    op.add_option("-s", "--save",
                  action="store_true",
                  default=False,
                  dest="save",
                  help="save results in different folders according to the relative stack size")
    op.add_option("-p", "--split",
                  action="store_true",
                  default=False,
                  dest="split",
                  help="split sattelit tournaments to round1 and round2")
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
    op.add_option("-n", "--notes",
                  action="store",
                  default=config["NOTES"],
                  dest="notes",
                  help="notes file"
                  " [default: %default]")
    op.add_option("-f", "--filter-chips",
                  action="store",
                  default="less",
                  dest="filter",
                  help="filter hands if one of the players has stack in chips: less, greater "
                  " [default: %default]")
    op.add_option("--bb-reg",
                  action="store_true",
                  default=False,
                  dest="bb_reg",
                  help="filter hands if player on Big Blind match regular label in notes file"
                  " [default: %default]")
    op.add_option("--sb-reg",
                  action="store_true",
                  default=False,
                  dest="sb_reg",
                  help="filter hands if player on Small Blind match regular label in notes file"
                  " [default: %default]")
    op.add_option("--bu-reg",
                  action="store_true",
                  default=False,
                  dest="bu_reg",
                  help="filter hands if player on Button match regular label in notes file"
                  " [default: %default]")
    (options, args) = op.parse_args()
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    if options.bb_reg or options.sb_reg or options.bu_reg:
        global notes
        notes = load_ps_notes(options.notes)
        logging.info('Player notes successfully loaded')
    if options.save:
        logging.info('Sorting by positions...')
        sort_by_tournament_position(options)
    elif options.split:
        logging.info('Splitting hand history files...')
        split(options)
    else:
        op.print_help()


if __name__ == '__main__':
    main()

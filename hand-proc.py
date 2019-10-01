"""parse hand history files and save to output dir according to tournament position"""
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
import logging
from optparse import OptionParser
import pprint
from pathlib import Path
from xml.dom import minidom
import json

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


def pass_filters(hh, options):
    """
    check if hand pass filters
    returns: boolean
    """
    passed = False
    if options.bb_reg:
        for player, pos in hh.positions().items():
            if pos == 'BB' and notes.get(player, 'uu') in config['REG_LABELS']:
                passed = True
                break
    else:
        passed = True
    return passed


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
    for txt in storage.read_hand():
        try:
            hh = PSHandHistory(txt)
        except Exception as e:
            logging.exception("%s " % e)
            continue

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

    for row in result:
        res_dir_path = output_dir_path.joinpath(row['pos_code'])
        res_file_path = res_dir_path.joinpath(row['fn']).with_suffix('.txt')
        res_file_path.write_text(row['txt'], encoding='utf-8')


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
    counter = 0
    skipped = 0
    round1_path = output_dir_path.joinpath(ROUND1_DIR).joinpath(str(counter))
    round2_path = output_dir_path.joinpath(ROUND2_DIR).joinpath(str(counter))
    round1_path.mkdir()
    round2_path.mkdir()
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
            logging.info(f'Processed {counter} of {len(file_list)}')
            round1_path = output_dir_path.joinpath(ROUND1_DIR).joinpath(str(counter))
            round2_path = output_dir_path.joinpath(ROUND2_DIR).joinpath(str(counter))
            round1_path.mkdir()
            round2_path.mkdir()

    logging.info(f'Finished: {counter}, skipped: {skipped}')


def main():
    load_config(config, CONFIG_FILE)

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
    (options, args) = op.parse_args()
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    if options.bb_reg:
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
        op.print_usage()


if __name__ == '__main__':
    main()

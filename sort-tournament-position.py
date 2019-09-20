"""parse hand history files and save to output dir according to tournament position"""
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
import logging
from optparse import OptionParser
import pprint
from pathlib import Path

CWD = Path.cwd()
DEFAULT_INPIT_DIR = 'input'
printer = pprint.PrettyPrinter()
DEFAULT_OUTPUT_DIR = 'output'


# this script filters hh of sats with 4 playrs tables, suits for 4max and for 3max
def sort_by_tournament_position(options):
    try:
        storage = HandStorage(options.input_dir)
    except IOError:
        logging.exception('Invalid input dir')
        try:
            storage = HandStorage(CWD.joinpath(DEFAULT_INPIT_DIR))
        except IOError:
            logging.exception('Default input dir doesnt exists')
            return

    output_dir_path = CWD.joinpath(options.output_dir)
    if not output_dir_path.exists():
        output_dir_path.mkdir()

    result = []
    pos_codes = set()
    for txt in storage.read_hand():
        try:
            hh = PSHandHistory(txt)
        except Exception as e:
            logging.exception("%s " % e)
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


def main(options):
    if options.save:
        sort_by_tournament_position(options)


if __name__ == '__main__':
    usage = "usage: %prog [options] arg1 arg2"
    op = OptionParser(usage=usage)
    op.add_option("-l", "--log", action="store", default=None,
                  dest="log",
                  help="log file")
    op.add_option("-s", "--save",
                  action="store_true",
                  default=True,
                  dest="save",
                  help="save results in different folders according to the relative stack size")
    op.add_option("-i", "--input",
                  action="store",
                  default="input",
                  dest="input_dir",
                  help="input directory "
                  " [default: %default]")
    op.add_option("-o", "--output",
                  action="store",
                  default="output",
                  dest="output_dir",
                  help="output directory "
                  " [default: %default]")
    op.add_option("-f", "--filter",
                  action="store",
                  default="less",
                  dest="filter",
                  help="filter hands if one of the players has stack: less, greater "
                  " [default: %default]")
    (options, args) = op.parse_args()
    logging.basicConfig(filename=options.log,
                        level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    if options.log:
        fh = logging.FileHandler(options.log)
        logger.addHandler(fh)
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    if len(args) == 0:
        op.print_help()
    main(options)

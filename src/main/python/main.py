from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import design
import sys
from collections import namedtuple
from pathlib import Path
from sat16ev import get_output_dir, get_tournament_id, split_sat_hh, add_round1_winner, fix_finishes_round1
from sat16ev import rename_tournament, change_bi, remove_win_entry_round2, fix_finishes_round2
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
from utils import get_path_dir_or_create, get_path_dir_or_error, load_config, save_config, get_ddmmyy_from_dt
from utils import load_ps_notes
import csv
import logging
import filters
import operator
import datetime

CWD = Path.cwd()
HandWriteEntry = namedtuple('HandWriteEntry', ['root_dir', 'file_name', 'text'])
logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S')
logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s] %(levelname).1s %(message)s')
fh = logging.FileHandler("handproc.log")
fh.setFormatter(formatter)
logger.addHandler(fh)

# TODO add filters to config
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

class PSGrandTourHistory(PSHandHistory):
    BOUNTY_WON_REGEX = "(?P<player>.*) wins \$(?P<bounty>.*) for eliminating "




class HandProcApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.toolButtonInput.clicked.connect(self.set_input_folder)
        self.toolButtonOutput.clicked.connect(self.set_output_folder)
        self.toolButtonNotes.clicked.connect(self.set_notes)
        self.pushButtonStart.clicked.connect(self.start)
        self.config = dict(config)
        self.config_file = 'handproc.cfg'
        try:
            new_config = load_config(self.config_file)
            self.config.update(new_config)
        except RuntimeError:
            pass
            # failed to open config
            self.statusBar().showMessage("Failed to open config file")

        self.lineEditInput.setText(self.config.get("INPUT", ''))
        self.lineEditOutput.setText(self.config.get("OUTPUT", ''))
        self.lineEditNotes.setText(self.config.get("NOTES", ''))
        self.hand_filter = filters.HandFilter()
        self.dteTo.setDateTime(datetime.datetime.now())
        # TODO load filters from config

    def set_notes(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   caption="Select Pokerstars Notes file",
                                                   directory=str(CWD),
                                                   filter="Xml files (*.xml)")
        if file_name:
            self.lineEditNotes.setText(file_name)
            self.config["NOTES"] = file_name

    def set_input_folder(self):

        dir = self.lineEditInput.text() if self.lineEditInput.text() else str(CWD)
        directory = QFileDialog.getExistingDirectory(self,
                                                     caption="Выберите папку",
                                                     directory=dir)

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEditInput.setText(directory)
            self.config["INPUT"] = directory

    def set_output_folder(self):
        dir = self.lineEditOutput.text() if self.lineEditOutput.text() else str(CWD)
        directory = QFileDialog.getExistingDirectory(self,
                                                     caption="Выберите папку",
                                                     directory=dir)

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEditOutput.setText(directory)
            self.config["OUTPUT"] = directory

    def set_hand_filter(self):
        self.hand_filter.clear()
        cond1 = filters.Condition('datetime', operator.ge, self.dteFrom.dateTime())
        cond2 = filters.Condition('datetime', operator.le, self.dteTo.dateTime())
        self.hand_filter.add_condition(cond1)
        self.hand_filter.add_condition(cond2)
        bi_from_cond = filters.Condition('bi', operator.ge, self.spinBoxBiFrom.value())
        bi_to_cond = filters.Condition('bi', operator.le, self.spinBoxBiTo.value())
        self.hand_filter.add_condition(bi_from_cond)
        self.hand_filter.add_condition(bi_to_cond)
        if self.checkBoxCoReg.isChecked():
            cond = filters.CORegFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxBuReg.isChecked():
            cond = filters.BURegFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxSbReg.isChecked():
            cond = filters.SBRegFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxBbReg.isChecked():
            cond = filters.BBRegFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxCoFish.isChecked():
            cond = filters.COFishFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxBuFish.isChecked():
            cond = filters.BUFishFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxSbFish.isChecked():
            cond = filters.SBFishFilter()
            self.hand_filter.add_condition(cond)

        if self.checkBoxBbFish.isChecked():
            cond = filters.BBFishFilter()
            self.hand_filter.add_condition(cond)

    def start(self):
        input_dir = self.lineEditInput.text()
        output_dir = self.lineEditOutput.text()
        notes_file = self.lineEditNotes.text()

        self.statusBar().showMessage(f'Processing hand histories...')

        if input_dir.strip() and output_dir.strip():
            Options = namedtuple('Options', ['input_dir', 'output_dir', 'notes_file'])
            o = Options(input_dir, output_dir, notes_file)
            if self.radioEv.isChecked():
                self.fix_hands_for_pt4(o)
            elif self.radioCsv.isChecked():
                self.stats(o)
            elif self.radioSplit.isChecked():
                self.split(o)
        else:
            self.statusBar().showMessage("Fill input and output directories!")

    def fix_hands_for_pt4(self, options):
        """ change original hand histories to load into pt4
        """
        # checking if there correct input ind output folders
        try:
            input_path = get_path_dir_or_error(self.config["INPUT"])
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(self.config["OUTPUT"])

        file_list = list(input_path.glob('**/*.txt'))
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_query = []
        round1_path = output_dir_path.joinpath(self.config['ROUND1_DIR'])
        round2_path = output_dir_path.joinpath(self.config['ROUND2_DIR'])
        self.progressBar.reset()
        self.progressBar.setRange(0, total)

        for file in file_list:
            counter += 1
            s = file.read_text(encoding='utf-8')
            tid = get_tournament_id(s)
            round1, round2 = split_sat_hh(s)
            if not round1 and not round2:
                skipped += 1
                continue
            dd, mm, yy = get_ddmmyy_from_hh(round1)
            text = ''
            root_dir_path = None
            prefix = self.config['ROUND1_PREFIX']
            if bool(round1 and round1.strip()):
                text = add_round1_winner(fix_finishes_round1(rename_tournament(round1, prefix)))
                root_dir_path = round1_path.joinpath(yy).joinpath(mm).joinpath(dd)
                entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
                hands_write_query.append(entry)

            if bool(round2 and round2.strip()):
                prefix = self.config['ROUND2_PREFIX']
                round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, prefix))))
                text = round2.replace("Round II", "Round I")
                root_dir_path = round2_path.joinpath(yy).joinpath(mm).joinpath(dd)
                entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
                hands_write_query.append(entry)

            self.progressBar.setValue(counter)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_query)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

    def save_hands(self, query):
        self.statusBar().showMessage(f'Writing hands...')
        self.progressBar.reset()
        self.progressBar.setRange(0, len(query))
        counter = 0
        for entry in query:
            dir_path = Path(entry.root_dir)
            dir_path.mkdir(parents=True, exist_ok=True)
            dir_path.joinpath(entry.file_name).write_text(entry.text, encoding='utf-8')
            counter += 1
            self.progressBar.setValue(counter)

    def stats(self, options):
        # counting statistics and saving in csv file

        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        storage = HandStorage(options.input_dir)
        total = len(list(storage.read_hand()))
        counter = 0

        self.statusBar().showMessage('Calculating...')
        self.progressBar.reset()
        self.progressBar.setRange(0, total)

        csv_columns = ['tid', 'hid', 'player', 'bounty', 'cnt']
        csv_file = "stats.csv"
        stats = []

        for txt in storage.read_hand():
            counter += 1
            try:
                hh = PSGrandTourHistory(txt)
            except Exception as e:
                self.statusBar().showMessage("%s " % e)
                continue
            self.progressBar.setValue(counter)
            try:
                bounty_won = hh.bounty_won
            except:
                self.statusBar().showMessage(hh.hid)
                return

            if bounty_won:
                tid = hh.tid
                hid = hh.hid
                for player, bounty in bounty_won.items():
                    stats.append({'tid': tid, 'hid': hid, 'player': player, 'bounty': bounty, 'cnt': 1})

        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                writer.writerows(stats)
        except IOError as e:
            self.statusBar().showMessage("%s " % e)

        self.statusBar().showMessage("Done!")

    def split(self, options):

        # checking input and output directories
        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        file_list = list(input_path.glob('**/*.txt'))
        # TODO need to exclude tournament summaries
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_query = []
        round1_path = output_dir_path.joinpath(config['ROUND1_DIR'])
        round2_path = output_dir_path.joinpath(config['ROUND2_DIR'])
        self.progressBar.reset()
        self.progressBar.setRange(0, total)
        self.set_hand_filter()
        notes = load_ps_notes(self.config["NOTES"])

        for file in file_list:
            s = file.read_text(encoding='utf-8')
            if not s:
                skipped += 1
                continue
            round1, round2 = split_sat_hh(s)

            round1hands = round1.strip().split('\n\n')
            for txt in round1hands:
                if bool(txt and txt.strip()):
                    try:
                        parsed = PSHandHistory(txt)
                        dd, mm, yy = get_ddmmyy_from_dt(parsed.datetime)
                    except Exception as e:
                        logger.exception('Exception %s while parsing file: %s', e, file)
                        logger.debug("hid: " + str(parsed.hid))
                        logger.debug("hh: " + parsed.hand_history)
                        continue
                    if self.hand_filter.check_conditions(parsed, notes=notes, config=self.config):
                        write_round1_path = round1_path.joinpath(yy).joinpath(mm).joinpath(dd)
                        entry = HandWriteEntry(write_round1_path,  parsed.hid + '.txt', txt)
                        hands_write_query.append(entry)

            if bool(round2 and round2.strip()):
                # sorting round2 by positions
                if self.checkBoxSort.isChecked():
                    hand_list = round2.strip().split('\n\n')
                    for txt in hand_list:
                        pos_str = '0'
                        try:
                            parsed = PSHandHistory(txt)
                        except Exception as e:
                            logger.exception('Exception %s while parsing file: %s', e, file)
                            self.statusBar().showMessage("%s " % e)
                            continue
                        if self.hand_filter.check_conditions(parsed, notes=notes, config=self.config):
                            try:
                                pos_str = self.get_positions_str(parsed)
                            except (RuntimeError, KeyError) as e:
                                logger.exception('Exception %s in get_position_str in file: %s', e, file)
                                continue
                            write_round2_path = round2_path.joinpath(pos_str).joinpath(yy).joinpath(mm).joinpath(dd)
                            entry = HandWriteEntry(write_round2_path, parsed.hid + '.txt', txt)
                            hands_write_query.append(entry)
                else:
                    write_round2_path = round2_path.joinpath(yy).joinpath(mm).joinpath(dd)
                    entry = HandWriteEntry(write_round2_path, file.name, round2)
                    hands_write_query.append(entry)

            counter += 1
            self.progressBar.setValue(counter)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_query)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

    def sort(self, options):
        # this script filters hh of sats with 4 playrs tables, suits for 4max and for 3max

        # checking input and output directories
        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        storage = HandStorage(input_path)
        result = []
        total = len(list(storage.read_hand()))
        counter = 0
        skipped = 0

        hands_write_query = []
        self.progressBar.reset()
        self.progressBar.setRange(0, total)
        self.statusBar().showMessage('Sorting hands...')
        for txt in storage.read_hand():
            try:
                hh = PSHandHistory(txt)
            except Exception as e:
                self.statusBar().showMessage("%s " % e)
                continue

            counter += 1
            self.progressBar.setValue(counter)
            # TODO add filters
            # if not pass_filters(hh, options):
            #     continue
            try:
                pos_str = self.get_positions_str(hh)
            except RuntimeError:
                continue

            entry = HandWriteEntry(output_dir_path.joinpath(pos_str), hh.hid + '.txt', txt)
            hands_write_query.append(entry)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_query)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

    @staticmethod
    def get_positions_str(hh):
        """ hh: parsed hand history instance of HandHistory
            returns: string with players tournament positions ex. "123" BU - 1, SB - 2, BB - 3.
        """
        positions = hh.positions()
        player_pos = {pos: hh.tournamentPosition(player) for player, pos in positions.items()}
        # for now only for 4 and 3 max
        if hh.players_number() == 4:
            pos_str = str(player_pos['CO']) + str(player_pos['BU']) + str(player_pos['SB']) + str(player_pos['BB'])
        elif hh.players_number() == 3:
            pos_str = str(player_pos['BU']) + str(player_pos['SB']) + str(player_pos['BB'])
        else:
            raise RuntimeError("Only 3 or 4 players supported")
        return pos_str

    def split_n_sort(self, options):
        pass

    def closeEvent(self, a0) -> None:
        # TODO save filters to config
        save_config(self.config, self.config_file)

    def check_input(self) -> None:

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = HandProcApp()
    window.show()
    app.exec_()      # 2. Invoke appctxt.app.exec_()

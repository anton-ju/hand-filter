from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
import design
import sys
import time
from threading import Event, Thread
from queue import Queue, Empty
from collections import namedtuple
from pathlib import Path
from sat16ev import get_output_dir, get_tournament_id, split_sat_hh, add_round1_winner, fix_finishes_round1
from sat16ev import rename_tournament, change_bi, remove_win_entry_round2, fix_finishes_round2
from sat16ev import modify_round1_hh, modify_round2_hh
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
from utils import get_path_dir_or_create, get_path_dir_or_error, load_config, save_config, get_ddmmyy_from_dt
from utils import load_ps_notes, get_dt_from_hh
from utils import Hand2NoteDB
import csv
import logging
import filters
import operator
import datetime
from typing import Dict, Callable, List, Generator, NamedTuple

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

VERSION = "0.3.4"
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
    'ROUND2_DIR': 'round2',
    'DB': 'Hand2Note3',
    'DATE_FROM': datetime.date(2020, 1, 1),
    'DATE_TO': datetime.date.today(),
    'SATS_ONLY': True,
    'SORT_ROUND1_HANDS': False,
}


class PSGrandTourHistory(PSHandHistory):
    BOUNTY_WON_REGEX = "(?P<player>.*) wins \$(?P<bounty>.*) for eliminating "


class RawHandHistory(NamedTuple):
    text: str
    file_name: str


class HandProcessor(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, int)
    writer_progress = pyqtSignal(int)

    def __init__(self, notes, config, hand_filter, path, hands_write_queue,
                 round1_func: Callable[[str], str]= lambda x: x,
                 round2_func: Callable[[str], str]= lambda x: x):
        """
        @parameter
            round1_modifier: function which exec on every hand round1 before send it to queue
            round1_modifier: function which exec on every hand round2 before send it to queue
        """
        self.notes = notes
        self.config = config
        self.hand_filter = hand_filter
        self.path = path
        self.hands_write_queue = hands_write_queue
        self.round1_func = round1_func
        self.round2_func = round2_func
        self.skipped = 0
        self.counter = 0
        self.writer_counter = 0
        self.round1_path = path.joinpath(config['ROUND1_DIR'])
        self.round2_path = path.joinpath(config['ROUND2_DIR'])
        super().__init__()

    def run(self, hist_iter):

        self.progress.emit(self.counter, self.skipped)
        self.writer_progress.emit(self.counter)
        # total = len(file_list)
        logger.debug("Hand processor started")
        for raw_history in hist_iter:
            QApplication.processEvents()
            if not raw_history.text:
                continue

            # TODO add tournament type detection. depend on detection split or not split,
            # to split by position s not only satellite hands
            self.process_raw_history(raw_history)

            self.progress.emit(self.counter, self.skipped)
        logger.debug("Hand processor finished")
        self.write_hands()
        self.finished.emit()

    def process_raw_history(self, raw_history: RawHandHistory):
        """divide raw hand history text into separate round1 and round2 hands

        """
        round1, round2 = split_sat_hh(raw_history.text, self.config['SATS_ONLY'])

        round1_hands = round1.strip().split('\n\n')
        round2_hands = round2.strip().split('\n\n')

        by_position = self.config["SORT_ROUND1_HANDS"]
        self.process_hands(round1_hands, raw_history.file_name, by_position=by_position, modifier=self.round1_func)
        # sorting round2 by positions
        self.process_hands(round2_hands, raw_history.file_name, by_position=True, modifier=self.round2_func)

    def write_hands(self):
        queue = self.hands_write_queue
        while not queue.empty():
            QApplication.processEvents()
            try:
                entry = queue.get_nowait()
                if entry:
                    self.write_entry(entry)
                    self.writer_counter += 1
                    self.writer_progress.emit(self.writer_counter)
            except Empty:
                logger.exception("Exception Empty")
            except Exception as e:
                if entry:
                    logger.exception('Exception %s while writing file: %s in dir: $s', e, entry.file_name, entry.root_dir)
                else:
                    logger.exception('Exception %s', e)

    @staticmethod
    def append_write_entry(path, yy, mm, dd, parsed, txt, hands_write_queue):
        write_path = path.joinpath(yy).joinpath(mm).joinpath(dd)
        entry = HandWriteEntry(write_path, parsed.hid + '.txt', txt)
        hands_write_queue.put_nowait(entry)

    @staticmethod
    def write_entry(entry):
        dir_path = Path(entry.root_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        dir_path.joinpath(entry.file_name).write_text(entry.text, encoding='utf-8')

    def process_hands(self, hands: List[str], file_name: str,
                      by_position: bool=False, modifier: Callable[[str], str] = lambda x: x):
        new_path = Path(self.path)
        for txt in hands:
            if bool(txt and txt.strip()):
                pos_str = '0'
                try:
                    parsed = PSHandHistory(txt)
                    dd, mm, yy = get_ddmmyy_from_dt(parsed.datetime)
                except Exception as e:
                    logger.exception('Exception %s while parsing file: %s', e, file_name)
                    logger.debug("hid: " + str(parsed.hid))
                    logger.debug("hh: " + parsed.hand_history)
                    continue
                if self.hand_filter.check_conditions(parsed, notes=self.notes, config=self.config):
                    self.counter += 1
                    if by_position:
                        try:
                            pos_str = get_positions_str(parsed)
                            new_path = self.path.joinpath(pos_str)
                        except (RuntimeError, KeyError) as e:
                            logger.exception('Exception %s in get_position_str in file: %s', e, file_name)
                            continue
                    txt = modifier(txt)
                    self.append_write_entry(new_path, yy, mm, dd, parsed, txt, self.hands_write_queue)
                else:
                    self.skipped += 1


# class HandWriter(QObject):
#     writer_finished = pyqtSignal()
#     progress = pyqtSignal(int)
#
#     def run(self, queue, finish_event):
#         # self.statusBar().showMessage(f'Writing hands...')
#         # self.progressBar.reset()
#         # self.progressBar.setRange(0, len(queue))
#         counter = 0
#         logger.debug("Hand writer started")
#         while True:
#             QApplication.processEvents()
#             try:
#                 if finish_event.is_set() and queue.empty():
#                     logger.debug("got event finished")
#                     break
#                 entry = queue.get_nowait()
#                 if entry:
#                     self.write_entry(entry)
#                     counter += 1
#                     self.progress.emit(counter)
#             except Empty:
#                 logger.exception("Exception Empty")
#                 time.sleep(5)
#             except Exception as e:
#                 if entry:
#                     logger.exception('Exception %s while writing file: %s in dir: $s', e, entry.file_name, entry.root_dir)
#                 else:
#                     logger.exception('Exception %s', e)
#
#         queue.task_done()
#         logger.debug("Hand writer finished")
#         self.writer_finished.emit()
#
#     def write_entry(self, entry):
#         dir_path = Path(entry.root_dir)
#         dir_path.mkdir(parents=True, exist_ok=True)
#         dir_path.joinpath(entry.file_name).write_text(entry.text, encoding='utf-8')


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


class HandProcApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.setWindowTitle(self.windowTitle() + " ::: " + VERSION)
        self.toolButtonInput.clicked.connect(self.set_input_folder)
        self.toolButtonOutput.clicked.connect(self.set_output_folder)
        self.toolButtonNotes.clicked.connect(self.set_notes)
        self.pushButtonStart.clicked.connect(self.start)
        self.pushButtonTestConn.clicked.connect(self.connect_db)
        self.checkBoxSort.stateChanged.connect(self.set_sort_all_hands)
        self.config = dict(config)
        self.config_file = 'handproc.cfg'
        try:
            new_config = load_config(self.config_file)
            self.config.update(new_config)
        except RuntimeError as e:
            logger.exception('Exception %s in HandProcApp.__init__', e)
            # failed to open config
            self.statusBar().showMessage("Failed to open config file")

        self.lineEditInput.setText(self.config.get("INPUT", ''))
        self.lineEditOutput.setText(self.config.get("OUTPUT", ''))
        self.lineEditNotes.setText(self.config.get("NOTES", ''))
        self.lineEditDBName.setText(self.config.get("DB", ''))
        self.checkBoxSort.setChecked(self.config.get("SORT_ROUND1_HANDS", False))
        # self.dteFrom.setDate(datetime.datetime.strptime(self.config.get("DATE_FROM", "2021-01-01"), '%Y-%m-%d'))
        # self.dteTo.setDate(datetime.datetime.strptime(self.config.get("DATE_TO", datetime.date.today().isoformat()), '%Y-%m-%d'))
        self.hand_filter = filters.HandFilter()
        self.dteTo.setDateTime(datetime.datetime.now())
        # TODO load filters from config

        self.hand_write_queue = Queue()

        self.db = None
        self.db_mode = False

    def set_sort_all_hands(self):
        self.config["SORT_ROUND1_HANDS"] = self.checkBoxSort.isChecked()

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
                                                     caption="Choose directory",
                                                     directory=dir)

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEditInput.setText(directory)
            self.config["INPUT"] = directory

    def set_output_folder(self):
        dir = self.lineEditOutput.text() if self.lineEditOutput.text() else str(CWD)
        directory = QFileDialog.getExistingDirectory(self,
                                                     caption="Choose directory",
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

    def connect_db(self):
        try:
            db = Hand2NoteDB(dbname=self.lineEditDBName.text())
            self.db = db
            self.config["DB"] = self.lineEditDBName.text()
            self.statusBar().showMessage(f'Successfully connected!')
        except Exception as e:
            logger.exception('Exception %s in HandProcApp.connect_db', e)
            self.statusBar().showMessage(f'Connection error!')


    @pyqtSlot(int, int)
    def report_processor_progress(self, counter, skipped):
        self.processorLabel.setText(f"Passed: {counter} Skipped: {skipped} Total: {counter + skipped}")

    @pyqtSlot(int)
    def report_writer_progress(self, value):
        self.writerLabel.setText(f"Write hands: {str(value)}")

    def input_is_filled(self) -> bool:
        is_filled = True
        input_dir = self.lineEditInput.text()
        output_dir = self.lineEditOutput.text()
        notes_file = self.lineEditNotes.text()
        if not notes_file.strip():
            self.show_msgbox(QMessageBox.Critical, "Fill notes file path")
            is_filled = False

        if not self.db_mode:
            if input_dir.strip() and output_dir.strip():
                is_filled = True
            else:
                self.show_msgbox(QMessageBox.Critical, "Fill input and output directories paths!")
                is_filled = False

        return is_filled

    def show_msgbox(self, msg_type, msg_text: str):
        msg_box = QMessageBox()
        msg_box.setIcon(msg_type)
        msg_box.setText(msg_text)
        msg_box.exec()

    def start(self):
        self.db_mode = False
        input_dir = self.lineEditInput.text()
        output_dir = self.lineEditOutput.text()
        notes_file = self.lineEditNotes.text()
        if self.tabWidget.currentIndex() == 1:
            self.db_mode = True
        else:
            self.db_mode = False

        if self.input_is_filled():
            self.statusBar().showMessage(f'Processing hand histories...')
            Options = namedtuple('Options', ['input_dir', 'output_dir', 'notes_file'])
            o = Options(input_dir, output_dir, notes_file)
            if self.radioEv.isChecked():
                self.split(o, fix=True)
            elif self.radioCsv.isChecked():
                self.stats(o)
            elif self.radioSplit.isChecked():
                self.split(o)

    def fix_hands_for_pt4(self, options):
        """ change original hand histories to load into pt4
        """
        # checking if there correct input ind output folders
        try:
            input_path = get_path_dir_or_error(self.config["INPUT"])
        except RuntimeError as e:
            self.show_msgbox(QMessageBox.Critical, 'Place hand history files in "input" directory')
            logger.exception('Exception %s in HandProcApp.fix_hands_for_pt4', e)
            return
        output_dir_path = get_path_dir_or_create(self.config["OUTPUT"])

        file_list = list(input_path.glob('**/*.txt'))
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_queue = Queue()
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
            dt = get_dt_from_hh(round1)
            dd, mm, yy = str(dt.day), str(dt.month), str(dt.year)
            text = ''
            root_dir_path = None
            prefix = self.config['ROUND1_PREFIX']
            if bool(round1 and round1.strip()):
                text = add_round1_winner(fix_finishes_round1(rename_tournament(round1, prefix)))
                root_dir_path = round1_path.joinpath(yy).joinpath(mm).joinpath(dd)
                entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
                hands_write_queue.put_nowait(entry)

            if bool(round2 and round2.strip()):
                prefix = self.config['ROUND2_PREFIX']
                round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, prefix))))
                text = round2.replace("Round II", "Round I")
                root_dir_path = round2_path.joinpath(yy).joinpath(mm).joinpath(dd)
                entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
                hands_write_queue.put_nowait(entry)

            self.progressBar.setValue(counter)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_queue)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')


    def save_hands(self, queue):
        # self.statusBar().showMessage(f'Writing hands...')
        # self.progressBar.reset()
        # self.progressBar.setRange(0, len(queue))
        counter = 0
        while not queue.empty():
            entry = queue.get()
            dir_path = Path(entry.root_dir)
            dir_path.mkdir(parents=True, exist_ok=True)
            dir_path.joinpath(entry.file_name).write_text(entry.text, encoding='utf-8')
            counter += 1
            # self.progressBar.setValue(counter)

    def stats(self, options):
        # counting statistics and saving in csv file

        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError as e:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            logger.exception('Exception %s in HandProcApp.stats', e)
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
            except Exception as e:
                logger.exception('Exception %s in HandProcApp.stats', e)
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
            logger.exception('Exception %s in HandProcApp.stats', e)
            self.statusBar().showMessage("%s " % e)

        self.statusBar().showMessage("Done!")

    def start_processor_thread(self, notes, output_dir_path,
                               round1_modifier: Callable[[str], str] = lambda x: x,
                               round2_modifier: Callable[[str], str] = lambda x: x):
        """ move calculations to separate thread to prevent GUI freeze
        notes: dict
        output_dit_path: path to output dir
        round1_modifier: function to exec before write hand history

        """

        self.thread1 = QThread()
        self.processor = HandProcessor(notes=notes,
                                       config=self.config,
                                       hand_filter=self.hand_filter,
                                       path=output_dir_path,
                                       hands_write_queue=self.hand_write_queue,
                                       round1_func= round1_modifier,
                                       round2_func=round2_modifier)

        # 2. Connect signals AFTER you move the object to its own thread
        self.processor.moveToThread(self.thread1)

        self.thread1.started.connect(
            lambda: self.processor.run(self.raw_histories_iter()))

        self.processor.finished.connect(self.thread1.quit)
        self.processor.finished.connect(self.processor.deleteLater)
        self.processor.progress.connect(self.report_processor_progress)
        self.processor.writer_progress.connect(self.report_writer_progress)
        self.thread1.finished.connect(self.thread1.deleteLater)

        self.thread1.finished.connect(
            lambda: self.pushButtonStart.setEnabled(True)
        )
        # self.thread1.finished.connect(
        #     lambda: self.progressBar.setValue(total)
        # )
        self.thread1.finished.connect(
            lambda:  self.show_msgbox(QMessageBox.Information, 'Done')
        )
        # self.thread1.finished.connect(
        #     lambda: finish_event.set()
        # )
        self.thread1.start()
        logger.debug("Thread1 started")

    # def start_writer_thread(self, finish_event):
    #
    #     self.thread2 = QThread()
    #     self.writer = HandWriter()
    #     # 2. Connect signals AFTER you move the object to its own thread
    #     self.writer.moveToThread(self.thread2)
    #
    #     self.thread2.started.connect(lambda: self.writer.run(self.hand_write_queue, finish_event))
    #
    #     self.writer.writer_finished.connect(self.thread2.quit)
    #     self.writer.writer_finished.connect(self.writer.deleteLater)
    #     self.writer.progress.connect(self.report_writer_progress)
    #
    #     self.thread2.finished.connect(self.thread2.deleteLater)
    #
    #
    #     self.thread2.start()
    #     logger.debug("Thread2 started")

    def raw_histories_iter(self) -> Generator[RawHandHistory, None, None]:
        """ returns sequience of RawHandHistory from db or from files from input path in self.config
        check self.db_mode and self.db if set to True then take hands from db else from path in self.config['INPUT']
        """
        if self.db_mode:
            if self.db:
                res = self.db.get_hh(self.dteFrom.dateTime(), self.dteTo.dateTime())
                # get_hh returns generator
            else:
                self.connect_db()
                if self.db:
                    for h in self.db.get_hh(self.dteFrom.dateTime(), self.dteTo.dateTime()):
                        yield RawHandHistory(h, 'DB')
                else:
                    return
        else:
            try:
                input_path = get_path_dir_or_error(self.config["INPUT"])
                for f in input_path.glob('**/*.txt'):
                    s = f.read_text(encoding='utf-8')
                    if not s:
                        continue
                    yield RawHandHistory(s, f.name)
            except RuntimeError as e:
                logger.exception('Exception %s in HandProcApp.split', e)
                self.show_msgbox(QMessageBox.Critical, 'Place hand history files in "input" directory')
                return

        return

    def split(self, options, fix=False):
        """split hand histories and save to files
        if fix set to True modifies hand histories for ev calculating"""

        output_dir_path = get_path_dir_or_create(options.output_dir)

        # TODO need to exclude tournament summaries
        # self.progressBar.reset()
        # self.progressBar.setRange(0, total)
        self.set_hand_filter()

        try:
            notes = load_ps_notes(self.config["NOTES"])
        except RuntimeError as e:
            logger.exception('Exception %s in HandProcApp.split', e)
            self.show_msgbox(QMessageBox.Critical, f'Error while loading notes /n {e}')
            return

        finish_event = Event()
        finish_event.clear()

        if fix:
            self.start_processor_thread(notes, output_dir_path, modify_round1_hh, modify_round2_hh)
        else:
            self.start_processor_thread(notes, output_dir_path)
        # self.start_writer_thread(finish_event)

        self.pushButtonStart.setEnabled(False)
        # self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')
        # todo add button stop

    def closeEvent(self, a0) -> None:
        # TODO save filters to config
        save_config(self.config, self.config_file)

    def check_input(self) -> None:

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = HandProcApp()
    window.show()
    sys.exit(app.exec_())      # 2. Invoke appctxt.app.exec_()
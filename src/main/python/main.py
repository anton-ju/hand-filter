from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import design
import sys
import time
from threading import Event, Thread
from queue import Queue, Empty
from collections import namedtuple
from pathlib import Path
from sat16ev import get_output_dir, get_tournament_id, split_sat_hh, add_round1_winner, fix_finishes_round1
from sat16ev import rename_tournament, change_bi, remove_win_entry_round2, fix_finishes_round2
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

VERSION = "0.3.2"
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
    'DATE_TO': datetime.date.today()
}


class PSGrandTourHistory(PSHandHistory):
    BOUNTY_WON_REGEX = "(?P<player>.*) wins \$(?P<bounty>.*) for eliminating "


class HandProcessor(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, int)
    writer_progress = pyqtSignal(int)

    def run(self, file_list, notes, options, hand_filter, path, hands_write_queue, from_file=False):

        skipped = 0
        counter = 0
        self.progress.emit(counter, skipped)
        self.writer_progress.emit(counter)
        # total = len(file_list)
        round1_path = path.joinpath(options['ROUND1_DIR'])
        round2_path = path.joinpath(options['ROUND2_DIR'])
        logger.debug("Hand processor started")
        for file in file_list:
            QApplication.processEvents()
            if from_file:
                s = file.read_text(encoding='utf-8')
                if not s:
                    skipped += 1
                    continue
            else:
                s = file
                file = "DB"
            round1, round2 = split_sat_hh(s)

            round1_hands = round1.strip().split('\n\n')
            self.process_hands(round1_hands, file, notes, options, hand_filter, round1_path, hands_write_queue)

            # sorting round2 by positions
            round2_hands = round2.strip().split('\n\n')
            self.process_hands(round2_hands, file, notes, options, hand_filter, round2_path,
                          hands_write_queue, by_position=True)

            counter += 1
            self.progress.emit(counter, skipped)
        logger.debug("Hand processor finished")
        self.write_hands(hands_write_queue)
        self.finished.emit()

    def write_hands(self, queue):
        counter = 0
        while not queue.empty():
            QApplication.processEvents()
            try:
                entry = queue.get_nowait()
                if entry:
                    self.write_entry(entry)
                    counter += 1
                    self.writer_progress.emit(counter)
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

    def process_hands(self, hands, file, notes, options, hand_filter, path, hands_write_query, by_position=False):
        new_path = Path(path)
        for txt in hands:
            if bool(txt and txt.strip()):
                pos_str = '0'
                try:
                    parsed = PSHandHistory(txt)
                    dd, mm, yy = get_ddmmyy_from_dt(parsed.datetime)
                except Exception as e:
                    logger.exception('Exception %s while parsing file: %s', e, file)
                    logger.debug("hid: " + str(parsed.hid))
                    logger.debug("hh: " + parsed.hand_history)
                    continue
                if hand_filter.check_conditions(parsed, notes=notes, config=options):
                    if by_position:
                        try:
                            pos_str = get_positions_str(parsed)
                            new_path = path.joinpath(pos_str)
                        except (RuntimeError, KeyError) as e:
                            logger.exception('Exception %s in get_position_str in file: %s', e, file)
                            continue
                    self.append_write_entry(new_path, yy, mm, dd, parsed, txt, hands_write_query)


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
        # self.dteFrom.setDate(datetime.datetime.strptime(self.config.get("DATE_FROM", "2021-01-01"), '%Y-%m-%d'))
        # self.dteTo.setDate(datetime.datetime.strptime(self.config.get("DATE_TO", datetime.date.today().isoformat()), '%Y-%m-%d'))
        self.hand_filter = filters.HandFilter()
        self.dteTo.setDateTime(datetime.datetime.now())
        # TODO load filters from config

        self.hand_write_queue = Queue()

        self.db = None

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

    def connect_db(self):
        try:
            db = Hand2NoteDB(dbname=self.lineEditDBName.text())
            self.db = db
            self.statusBar().showMessage(f'Successfully connected!')
        except Exception as e:
            logger.exception('Exception %s in HandProcApp.connect_db', e)
            self.statusBar().showMessage(f'Connection error!')


    @pyqtSlot(int, int)
    def report_processor_progress(self, counter, skipped):
        self.processorLabel.setText(f"Processed files: {counter}  Skipped: {skipped}")

    @pyqtSlot(int)
    def report_writer_progress(self, value):
        self.writerLabel.setText(f"Wrote hands: {str(value)}")

    def input_is_filled(self) -> bool:
        input_dir = self.lineEditInput.text()
        output_dir = self.lineEditOutput.text()
        notes_file = self.lineEditNotes.text()
        if not notes_file.strip():
            self.statusBar().showMessage("Fill notes file path")
            return False
        if self.tabWidget.currentIndex() != 1:
            if input_dir.strip() and output_dir.strip():
                self.statusBar().showMessage("Fill input and output directories paths!")
            return False
        return True

    def start(self):
        input_dir = self.lineEditInput.text()
        output_dir = self.lineEditOutput.text()
        notes_file = self.lineEditNotes.text()

        self.statusBar().showMessage(f'Processing hand histories...')
        if self.input_is_filled():
            Options = namedtuple('Options', ['input_dir', 'output_dir', 'notes_file'])
            o = Options(input_dir, output_dir, notes_file)
            if self.radioEv.isChecked():
                self.fix_hands_for_pt4(o)
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
            self.statusBar().showMessage('Place hand history files in "input" directory')
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

    def start_processor_thread(self, file_list, notes, output_dir_path, total, finish_event, from_file=False):

        self.thread1 = QThread()
        self.processor = HandProcessor()

        # 2. Connect signals AFTER you move the object to its own thread
        self.processor.moveToThread(self.thread1)

        self.thread1.started.connect(
            lambda: self.processor.run(file_list, notes, self.config, self.hand_filter, output_dir_path,
                                       self.hand_write_queue, from_file))

        self.processor.finished.connect(self.thread1.quit)
        self.processor.finished.connect(self.processor.deleteLater)
        self.processor.progress.connect(self.report_processor_progress)
        self.processor.writer_progress.connect(self.report_writer_progress)
        self.thread1.finished.connect(self.thread1.deleteLater)

        self.thread1.finished.connect(
            lambda: self.pushButtonStart.setEnabled(True)
        )
        self.thread1.finished.connect(
            lambda: self.progressBar.setValue(total)
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

    def split(self, options):

        from_file = True
        # checking input and output directories
        # if visible tab 1 then take hands from db
        # else from disk
        if self.tabWidget.currentIndex() == 1:
            if self.db:
                file_list = list(self.db.get_hh(self.dteFrom.dateTime(), self.dteTo.dateTime()))
                from_file = False
                # get_hh returns generator
            else:
                self.connect_db()
                if self.db:
                    file_list = list(self.db.get_hh(self.dteFrom.dateTime(), self.dteTo.dateTime()))
                    from_file = False
                else:
                    return
        else:
            try:
                input_path = get_path_dir_or_error(options.input_dir)
                file_list = list(input_path.glob('**/*.txt'))
            except RuntimeError as e:
                logger.exception('Exception %s in HandProcApp.split', e)
                self.statusBar().showMessage('Place hand history files in "input" directory')
                return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        # TODO need to exclude tournament summaries
        total = len(file_list)
        self.progressBar.reset()
        self.progressBar.setRange(0, total)
        self.set_hand_filter()
        try:

            notes = load_ps_notes(self.config["NOTES"])
        except RuntimeError as e:
            logger.exception('Exception %s in HandProcApp.split', e)
            self.statusBar().showMessage(e)

        finish_event = Event()
        finish_event.clear()
        self.start_processor_thread(file_list, notes, output_dir_path, total, finish_event, from_file)
        # self.start_writer_thread(finish_event)

        self.pushButtonStart.setEnabled(False)
        # self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

    def sort(self, options):
        # this script filters hh of sats with 4 playrs tables, suits for 4max and for 3max

        # checking input and output directories
        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError as e:
            logger.exception('Exception %s in HandProcApp.sort', e)
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
                logger.exception('Exception %s in HandProcApp.sort', e)
                self.statusBar().showMessage("%s " % e)
                continue

            counter += 1
            self.progressBar.setValue(counter)
            # TODO add filters
            # if not pass_filters(hh, options):
            #     continue
            try:
                pos_str = get_positions_str(hh)
            except RuntimeError as e:
                logger.exception('Exception %s in HandProcApp.sort', e)
                continue

            entry = HandWriteEntry(output_dir_path.joinpath(pos_str), hh.hid + '.txt', txt)
            hands_write_query.append(entry)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_query)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

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
    sys.exit(app.exec_())      # 2. Invoke appctxt.app.exec_()

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import design
import sys
from collections import namedtuple
from pathlib import Path
from sat16ev import get_output_dir, get_tournament_id, split_sat_hh, add_round1_winner, fix_finishes_round1
from sat16ev import rename_tournament, change_bi, remove_win_entry_round2, fix_finishes_round2
from pypokertools.parsers import PSHandHistory
from pypokertools.storage.hand_storage import HandStorage
from utils import get_path_dir_or_create, get_path_dir_or_error, load_config, save_config
import csv

CWD = Path.cwd()
HandWriteEntry = namedtuple('HandWriteEntry', ['root_dir', 'file_name', 'text'])

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
        self.config.update(load_config(self.config_file))
        self.lineEditInput.setText(self.config.get("INPUT", ''))
        self.lineEditOutput.setText(self.config.get("OUTPUT", ''))
        self.lineEditNotes.setText(self.config.get("NOTES", ''))
        # TODO load_config from config file

    def set_notes(self):
        file_name, _ = QFileDialog.getOpenFileName(self,
                                                   caption="Select Pokerstars Notes file",
                                                   directory=str(CWD),
                                                   filter="Xml files (*.xml)")
        if file_name:
            self.lineEditNotes.setText(file_name)

    def set_input_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEditInput.setText(directory)

    def set_output_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку")

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.lineEditOutput.setText(directory)

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
            elif self.radioSort.isChecked():
                self.sort(o)
        else:
            self.statusBar().showMessage("Fill input and output directories!")

    def fix_hands_for_pt4(self, options):
        """ change original hand histories to load into pt4
        """
        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        file_list = list(input_path.glob('**/*.txt'))
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_query = []
        round1_path = output_dir_path.joinpath(config['ROUND1_DIR']).joinpath(str(counter))
        round2_path = output_dir_path.joinpath(config['ROUND2_DIR']).joinpath(str(counter))
        self.progressBar.reset()
        self.progressBar.setRange(0, total)

        for file in file_list:
            s = file.read_text(encoding='utf-8')
            tid = get_tournament_id(s)
            round1, round2 = split_sat_hh(s)
            if not round1 and not round2:
                skipped += 1
                counter += 1
                continue
            text = ''
            root_dir_path = None
            prefix = config['ROUND1_PREFIX']
            if round1:
                text = add_round1_winner(fix_finishes_round1(rename_tournament(round1, prefix)))
                root_dir_path = round1_path

            if round2:
                prefix = config['ROUND2_PREFIX']
                round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, prefix))))
                text = round2.replace("Round II", "Round I")
                root_dir_path = round2_path

            hh = PSHandHistory(text)
            dd = str(hh.datetime.day)
            mm = str(hh.datetime.month)
            yy = str(hh.datetime.year)
            root_dir_path = root_dir_path.joinpath(yy).joinpath(mm).joinpath(dd)
            entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
            hands_write_query.append(entry)

            counter += 1
            if counter % 100 == 0:
                self.progressBar.setValue(counter)
                round1_path = output_dir_path.joinpath(config['ROUND1_DIR']).joinpath(str(counter))
                round2_path = output_dir_path.joinpath(config['ROUND2_DIR']).joinpath(str(counter))
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
            # TODO add filters check
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
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_query = []
        round1_path = output_dir_path.joinpath(config['ROUND1_DIR'])
        round2_path = output_dir_path.joinpath(config['ROUND2_DIR'])
        self.progressBar.reset()
        self.progressBar.setRange(0, total)

        for file in file_list:
            s = file.read_text(encoding='utf-8')
            round1, round2 = split_sat_hh(s)
            s = round1.split('\n\n')
            # determine date and time by first hand in tournament
            hh = None
            for text in s:
                try:
                    hh = PSHandHistory(text)
                    dd = str(hh.datetime.day)
                    mm = str(hh.datetime.month)
                    yy = str(hh.datetime.year)
                except Exception as e:
                    self.statusBar().showMessage(f'{e}')
                break

            if not hh:
                skipped += 1
                continue
            write_round1_path = round1_path.joinpath(yy).joinpath(mm).joinpath(dd)
            write_round2_path = round2_path.joinpath(yy).joinpath(mm).joinpath(dd)
            if round1:
                entry = HandWriteEntry(write_round1_path, file.name, round1)
                hands_write_query.append(entry)

            if round2:
                entry = HandWriteEntry(write_round2_path, file.name, round2)
                hands_write_query.append(entry)

            counter += 1
            self.progressBar.setValue(counter)

        self.progressBar.setValue(total)
        self.save_hands(hands_write_query)
        self.statusBar().showMessage(f'Total hands processed: {counter}, skipped: {skipped}')

    def sort(self, options):
        pass

    def closeEvent(self, a0) -> None:
        # TODO save_config to file
        save_config(self.config, self.config_file)

    def check_input(self) -> None:

        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = HandProcApp()
    window.show()
    app.exec_()      # 2. Invoke appctxt.app.exec_()

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
import design
import sys
from collections import namedtuple
from pathlib import Path
from sat16ev import get_output_dir, get_tournament_id, split_sat_hh, config, add_round1_winner, fix_finishes_round1
from sat16ev import rename_tournament, change_bi, remove_win_entry_round2, fix_finishes_round2
from utils import get_path_dir_or_create, get_path_dir_or_error

CWD = Path.cwd()


class HandProcApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.toolButtonInput.clicked.connect(self.set_input_folder)
        self.toolButtonOutput.clicked.connect(self.set_output_folder)
        self.pushButtonStart.clicked.connect(self.start)

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

        self.statusBar().showMessage(f'Processing hand histories...')

        if input_dir.strip() and output_dir.strip():
            Options = namedtuple('Options', ['input_dir', 'output_dir'])
            o = Options(input_dir, output_dir)
            if self.radioEv.isChecked():
                self.fix_hands_for_pt4(o)

    def fix_hands_for_pt4(self, options):
        """ change original hand histories to load into pt4
        """
        try:
            input_path = get_path_dir_or_error(options.input_dir)
        except RuntimeError:
            self.statusBar().showMessage('Place hand history files in "input" directory')
            return
        output_dir_path = get_path_dir_or_create(options.output_dir)

        # round1_path = output_dir_path.joinpath(config['ROUND1_DIR'])
        # if not round1_path.exists():
        #   round1_path.mkdir()
        # round2_path = output_dir_path.joinpath(config['ROUND2_DIR'])
        # if not round2_path.exists():
            # round2_path.mkdir()

        file_list = list(input_path.glob('**/*.txt'))
        total = len(file_list)
        counter = 0
        skipped = 0
        hands_write_query = []
        HandWriteEntry= namedtuple('HandWriteEntry', ['root_dir', 'file_name', 'text'])
        round1_path = output_dir_path.joinpath(config['ROUND1_DIR']).joinpath(str(counter))
        round2_path = output_dir_path.joinpath(config['ROUND2_DIR']).joinpath(str(counter))
        # round1_path.mkdir()
        # round2_path.mkdir()
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
                # round1_path.joinpath(prefix + file.name).write_text(round1, encoding='utf-8')

            if round2:
                prefix = config['ROUND2_PREFIX']
                round2 = change_bi(remove_win_entry_round2(fix_finishes_round2(rename_tournament(round2, prefix))))
                text = round2.replace("Round II", "Round I")
                root_dir_path = round2_path
                # round2_path.joinpath(prefix + file.name).write_text(round2, encoding='utf-8')

            entry = HandWriteEntry(root_dir_path, prefix + file.name, text)
            hands_write_query.append(entry)

            counter += 1
            if counter % 100 == 0:
                self.progressBar.setValue(counter)
                round1_path = output_dir_path.joinpath(config['ROUND1_DIR']).joinpath(str(counter))
                round2_path = output_dir_path.joinpath(config['ROUND2_DIR']).joinpath(str(counter))
                # round1_path.mkdir()
                # round2_path.mkdir()
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



if __name__ == '__main__':
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = HandProcApp()
    window.show()
    app.exec_()      # 2. Invoke appctxt.app.exec_()

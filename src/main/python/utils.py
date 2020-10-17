from pathlib import Path
import json
from typing import List
from pypokertools.parsers import PSHandHistory


def load_config(config_file):
    try:
        with open(config_file, 'r') as f:
            config_json = f.read()
            if config_json == '':
                return []
            return json.loads(config_json, encoding='utf-8')
    except IOError:
        raise RuntimeError("Config file opening error")
    except json.JSONDecodeError:
        raise RuntimeError("Config file decode error")


def save_config(config_current, config_file):
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            config_json = json.dumps(config_current)
            if config_json == '':
                return
            f.write(config_json)
    except IOError:
        raise RuntimeError("Config file saving error")
    except json.JSONDecodeError:
        raise RuntimeError("Config file saving error")


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


def get_path_dir_or_create(path):
    output_dir_path = Path(path)
    if output_dir_path.exists():
        return output_dir_path

    output_dir_path = Path.cwd().joinpath(path)
    if not output_dir_path.exists():
        output_dir_path.mkdir()
    return output_dir_path


def get_path_dir_or_error(path):
    output_dir_path = Path(path)
    if output_dir_path.exists():
        return output_dir_path

    output_dir_path = Path.cwd().joinpath(path)
    if not output_dir_path.exists():
        raise RuntimeError('Path does not exists')


def get_ddmmyy_from_hh(hh: str):
    """returns (dd, mm, yy) from hand history file"""
    s = hh.split('\n\n')
    # determine date and time by first hand in tournament
    hh = None
    dd, mm, yy = ('', '', '')
    for text in s:
        try:
            # if None or empty string take next element
            if not bool(text and text.strip()):
                continue
            # print(f'text: {text}')
            hh = PSHandHistory(text)
            dd = str(hh.datetime.day)
            mm = str(hh.datetime.month)
            yy = str(hh.datetime.year)
            break
        except Exception as e:
            pass

    return dd, mm, yy

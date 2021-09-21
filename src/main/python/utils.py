from pathlib import Path
import json
from typing import List, Dict
from pypokertools.parsers import PSHandHistory
from datetime import datetime
import logging
from xml.dom import minidom
import psycopg2
logger = logging.getLogger(__name__)


class Hand2NoteDB():
    def __init__(self, dbname='Hand2Note3', user='postgres', host='127.0.0.1', port='5318', pwd=''):
        # try:
            self.conn = psycopg2.connect(
                f"dbname='{dbname}' user='{user}' host='{host}' port='{port}'")
        # except:
        #     raise psycopg2.Error('Connection error')

    def get_hh(self, start_date=datetime(2000, 1, 1), end_date=None):

        if end_date is None:
            end_date = datetime.today()
        sql = " SELECT hh_id, date_played, room_id, gamenumber, hh FROM public.handhistory WHERE date_played BETWEEN %s AND %s; "
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, (start_date.toPyDateTime(), end_date.toPyDateTime()))
                for record in cur:
                    yield record[4]

    def get_summary(self, tid):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT tournament_id, summary "
                            "FROM tournament_summaries "
                            f"WHERE tournament_id = {tid}")
                if cur.rowcount > 0:
                    return cur.fetchone()[1]
                else:
                    return None


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
            config_json = json.dumps(config_current, default=str)
            if config_json == '':
                return
            f.write(config_json)
    except IOError:
        raise RuntimeError("Config file saving error")
    except json.JSONDecodeError:
        raise RuntimeError("Config file saving error")


def load_ps_notes(notes_file) -> Dict[str, str]:
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


def get_dt_from_hh(hh: str):
    """returns (dd, mm, yy) from hand history file"""
    s = hh.split('\n\n')
    # determine date and time by first hand in tournament
    hh = None
    dt = datetime.now()
    for text in s:
        try:
            # if None or empty string take next element
            if not bool(text and text.strip()):
                continue
            # print(f'text: {text}')
            hh = PSHandHistory(text)
            dt = hh.datetime
            break
        except Exception as e:
            logger.exception('hand id: %s, tournament id: %s', hh.hid, hh.tid)

    return dt

def get_ddmmyy_from_dt(dt: datetime):
    """returns (dd, mm, yy) from datetime"""
    try:
        dd = str(dt.day)
        mm = str(dt.month)
        yy = str(dt.year)
    except Exception as e:
        logger.exception(e)
    return dd, mm, yy



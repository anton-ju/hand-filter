from pathlib import Path
import json


def load_config(config_current, config_file):
    with open(config_file, 'r') as f:
        config_json = f.read()
        if config_json == '':
            return
        new_config = json.loads(config_json, encoding='utf-8')
        if new_config:
            config_current.update(new_config)


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

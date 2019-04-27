from pathlib import Path

FILE_PATH = Path(__file__)

ROOT_DIR = FILE_PATH.resolve().parent

TEMP_DIR = ROOT_DIR.joinpath("temp")

from files.file import File
from files.sound import SoundFile


def path_to_file(path: str):
    return File(path)


def path_to_sound(path: str):
    return SoundFile.from_path(path)


def keep_path_only(path: str):
    return path

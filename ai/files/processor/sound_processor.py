from typing import ClassVar, NoReturn

from files.processor import DatasetItemProcessor
from files.file import File
from os import path, makedirs
import json

from files.sound import SoundFile


class SoundProcessor(DatasetItemProcessor[File, dict]):
    # Versioning support (when SoundProcessor gets extended this should be changed as well)
    version: ClassVar[str] = "0.0.1"

    # Caching directory (must be a valid folder)
    cache_dir: str
    # Cache working directory (takes into account versioning)
    cache_wd: str

    def raise_permission_error(self, reason: str) -> NoReturn:
        raise Exception('Not enough permission to {}'.format(reason))

    def cache_working_directory(self, cache_dir: str):
        return path.join(cache_dir, self.version)

    def __init__(self, cache_dir: str):
        super().__init__()
        self.cache_dir = cache_dir
        self.cache_wd = self.cache_working_directory(cache_dir)
        if not path.exists(self.cache_wd) or not path.isdir(self.cache_wd):
            try:
                makedirs(self.cache_wd)
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')

    @classmethod
    def init(cls, cache_dir: str, version: str = "0.0.1"):
        cls.version = version
        return cls(cache_dir)

    def cache_location(self, file: File):
        return path.join(self.cache_wd, file.identity())

    def is_cached(self, file: File):
        cache_location = self.cache_location(file)
        return path.exists(cache_location) and path.isdir(cache_location)

    def get_cache(self, file):
        # TODO return cached data
        return {}

    def cache(self, file: File, data: dict) -> bool | None:
        cache_location = self.cache_location(file)
        try:
            makedirs(cache_location)
        except Exception as e:
            print(e)
            self.raise_permission_error('create necessary caching directories')
        # TODO cache data accordingly (serialize stuff)
        return None

    def process(self, file: File):
        # TODO process file and return a T
        with SoundFile.from_file(file) as sound:
            pass

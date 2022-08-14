from typing import ClassVar, NoReturn

import numpy as np
from numpy import ndarray

from files.processor import DatasetItemProcessor
from files.file import File
from os import path, makedirs, remove
import json

from files.json import NpEncoder, NpDecoder
from files.sound import SoundFile


ND_ARRAY_FIELDS = ['stft', 'mfcc', 'chroma', 'chroma_cens', 'mel', 'contrast', 'spectral_bandwidth', 'tonnetz']


class SoundProcessor(DatasetItemProcessor[File, dict[str, ndarray]]):
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
        return path.join(self.cache_wd, file.identity)

    def data_file(self, file: File):
        return path.join(self.cache_location(file), 'data.json')

    def is_cached(self, file: File):
        cache_location = self.cache_location(file)
        data_file = self.data_file(file)
        resources_exist = path.exists(cache_location) and path.exists(data_file)
        valid_resources = path.isdir(cache_location) and path.isfile(data_file)
        return resources_exist and valid_resources

    def get_cache(self, file) -> dict[str, ndarray]:
        data_file = self.data_file(file)
        with open(data_file, 'r') as json_file:
            data = json.load(json_file, cls=NpDecoder)

            corrected = {}
            for key, value in data.items():
                if key in ND_ARRAY_FIELDS:
                    # TODO this currently works, but it might be slow for huge arrays
                    #   because all ndarrays are huge, the JSON encoder wastes time cycling through array items
                    #   and constructing normal arrays, just to be converted to np arrays (thankfully NOT copied)
                    # SEE: https://numpy.org/doc/stable/reference/generated/numpy.save.html
                    # Current performance
                    # Uncached  0.97163947199805990s
                    # Cached    0.07287374799852842s
                    # 92,4999189413% faster for a 4.4MiB json file
                    corrected[key] = np.asarray(value)
                else:
                    corrected[key] = value
            return corrected

    def cache(self, file: File, data: dict[str, ndarray]) -> bool | None:
        cache_location = self.cache_location(file)
        if not path.exists(cache_location):
            try:
                makedirs(cache_location)
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')
        data_file = self.data_file(file)

        try:
            with open(data_file, 'w') as df:
                json.dump(data, df, check_circular=False, cls=NpEncoder)
        except Exception as e:
            print(e)
            try:
                remove(data_file)
            finally:
                return False
        return True

    def process(self, file: File) -> dict[str, ndarray]:
        with SoundFile.from_file(file) as sound:
            return sound.features()

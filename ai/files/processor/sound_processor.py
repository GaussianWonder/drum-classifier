from typing import ClassVar, NoReturn, Any

import numpy as np
from numpy import ndarray

from files.processor import DatasetItemProcessor
from files.file import File
from os import path, makedirs, remove, listdir
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
        if not path.exists(cache_location):
            return False

        data_file = self.data_file(file)
        if path.exists(data_file) and not path.isfile(data_file):
            return False

        return len(listdir(cache_location)) > 0

    def get_cache(self, file) -> dict[str, ndarray]:
        cache_location = self.cache_location(file)
        data_file = self.data_file(file)
        loaded_from_data: dict[str, Any] = {}
        ndarrays: dict[str, ndarray] = {}

        if path.exists(data_file):
            with open(data_file, 'r') as json_file:
                data = json.load(json_file, cls=NpDecoder)

                for key, value in data.items():
                    if key in ND_ARRAY_FIELDS:
                        # NDARRAYS in json currently works, but it might be slow for huge arrays
                        #   because all ndarrays are huge, the JSON encoder wastes time cycling through array items
                        #   and constructing normal arrays, just to be converted to np arrays (thankfully NOT copied)
                        # SEE: https://numpy.org/doc/stable/reference/generated/numpy.save.html
                        # Current performance for ndarrays in json
                        # Uncached  0.97163947199805990s
                        # Cached    0.07287374799852842s  <--
                        # 92,4999189413% faster for a 4.4MiB json file
                        loaded_from_data[key] = np.asarray(value)
                    else:
                        loaded_from_data[key] = value

        for nd_arr_field in ND_ARRAY_FIELDS:
            # To avoid NDARRAYS in json, provide all ndarray fields to ND_ARRAY_FIELDS
            #   that will cover both serialization and deserialization
            # All NDARRAYS must be at the root(top) level of the dictionary
            # Current performance for ndarrays serialized and deserialized individually
            # UncachedJ 0.9716394719980599000s
            # Uncached  0.6433532139999443000s
            # Cached    0.0016425220019300468s
            # CachedJ   0.0728737479985284200s
            #
            # 99,7446935888% faster loading time cached, and 97,7460717377% faster load time compared to CachedJ
            # 33,7868383757% faster generation time (due to not serializing huge arrays in json when caching)

            ndarrays[nd_arr_field] = np.load(path.join(cache_location, '{}.npy'.format(nd_arr_field)))

        return {**ndarrays, **loaded_from_data}

    def cache(self, file: File, data: dict[str, ndarray]) -> bool | None:
        cache_location = self.cache_location(file)
        if not path.exists(cache_location):
            try:
                makedirs(cache_location)
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')
        data_file = self.data_file(file)
        remaining: dict[str, Any] = {}

        try:
            for key, value in data.items():
                if isinstance(value, ndarray):
                    np.save(
                        path.join(cache_location, '{}.npy'.format(key)),
                        data[key],
                    )
                else:
                    remaining[key] = value

            if len(remaining.keys()) > 0:
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

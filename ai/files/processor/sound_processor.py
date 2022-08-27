import librosa  # type: ignore
import librosa.display  # type: ignore
from matplotlib import pyplot as plt  # type: ignore

from shutil import rmtree
from typing import ClassVar, NoReturn
from os import path, makedirs
import json

import numpy as np
from numpy import ndarray

import preferences
from files.processor import DatasetItemProcessor
from files.file import File

from files.json import NpEncoder, NpDecoder
from files.processor.typings import SPT, NestedBaseVals
from files.sound import SoundFile

# TODO pick relevant features
ND_ARRAY_FIELDS = ['stft', 'mfcc', 'chroma', 'chroma_cens', 'mel', 'contrast', 'spectral_bandwidth', 'tonnetz']


# TODO see np.load and np.save, maybe `allow_pickle` should be False someday


class SoundProcessor(DatasetItemProcessor[File, SPT]):
    # Versioning support (when SoundProcessor gets extended this should be changed as well)
    version: ClassVar[str] = "0.0.1"

    # Caching directory (must be a valid folder)
    cache_dir: str
    # Cache working directory (takes into account versioning)
    cache_wd: str
    # Plots are not always needed or queried, but when they are, cache them
    # This also checks for plots on already (impartial) cached data
    cache_plots: bool

    def raise_permission_error(self, reason: str) -> NoReturn:
        raise Exception('Not enough permission to {}'.format(reason))

    def cache_working_directory(self, cache_dir: str):
        return path.join(cache_dir, self.version)

    def __init__(self, cache_dir: str, cache_plots: bool):
        super().__init__()
        self.cache_dir = cache_dir
        self.cache_wd = self.cache_working_directory(cache_dir)
        self.cache_plots = cache_plots
        if not path.exists(self.cache_wd) or not path.isdir(self.cache_wd):
            try:
                makedirs(self.cache_wd)
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')

    @classmethod
    def init(cls, cache_dir: str, cache_plots: bool = False, version: str = "0.0.1"):
        cls.version = version
        return cls(cache_dir, cache_plots)

    def cache_location(self, file: File):
        return path.join(self.cache_wd, file.identity)

    def plot_location(self, file: File):
        return path.join(self.cache_location(file), 'plots')

    def data_file(self, file: File):
        return path.join(self.cache_location(file), 'data.json')

    def plot_files(self, file: File):
        plot_location = self.plot_location(file)
        return [path.join(plot_location, '{}.png'.format(p)) for p in ND_ARRAY_FIELDS]

    def are_plots_cached(self, file: File):
        plot_location = self.plot_location(file)
        if not path.exists(plot_location):
            return False

        return all([path.exists(p) and path.isfile(p) for p in self.plot_files(file)])

    def nd_array_files(self, file: File):
        cache_location = self.cache_location(file)
        return [path.join(cache_location, '{}.npy'.format(p)) for p in ND_ARRAY_FIELDS]

    def cache_plot_files(self, file: File, data: SPT):
        plot_location = self.plot_location(file)
        if not path.exists(plot_location):
            try:
                makedirs(plot_location)
                makedirs(path.join(plot_location, 'amp_to_db'))
                # makedirs(path.join(plot_location, 'log_pow'))
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')

        sr = data['info']['sample_rate']  # type: ignore
        for plot_key in ND_ARRAY_FIELDS:
            plot_and_save(
                data=data[plot_key],
                sr=sr,
                file_path=path.join(plot_location, '{}.png'.format(plot_key)),
            )
            plot_and_save(
                data=librosa.amplitude_to_db(data[plot_key], ref=np.max),
                sr=sr,
                file_path=path.join(plot_location, 'amp_to_db', '{}.png'.format(plot_key)),
            )
            # plot_and_save(
            #     data=librosa.power_to_db(data[plot_key]**2, ref=np.max),  # type: ignore
            #     sr=sr,
            #     file_path=path.join(plot_location, 'log_pow', '{}.png'.format(plot_key)),
            # )

    # ABSTRACT METHODS IMPL
    def is_cached(self, file: File):
        cache_location = self.cache_location(file)
        if not path.exists(cache_location):
            return False

        data_file = self.data_file(file)
        if path.exists(data_file) and not path.isfile(data_file):
            return False

        return all([path.exists(p) and path.isfile(p) for p in self.nd_array_files(file)])

    def get_cache(self, file) -> SPT:
        cache_location = self.cache_location(file)
        data_file = self.data_file(file)
        from_data: dict[str, int | float] = {}
        ndarrays: dict[str, ndarray] = {}

        if path.exists(data_file):
            with open(data_file, 'r') as json_file:
                from_data = json.load(json_file, cls=NpDecoder)
                # NDARRAYS in json currently works, but it might be slow for huge arrays
                #   because all ndarrays are huge, the JSON encoder wastes time cycling through array items
                #   and constructing normal arrays, just to be converted to np arrays (thankfully NOT copied)
                # SEE: https://numpy.org/doc/stable/reference/generated/numpy.save.html
                # Current performance for ndarrays in json
                # Uncached  0.97163947199805990s
                # Cached    0.07287374799852842s  <--
                # 92,4999189413% faster for a 4.4MiB json file
                # loaded_from_data[key] = np.asarray(value)

        for nd_arr_field in ND_ARRAY_FIELDS:
            ndarrays[nd_arr_field] = np.load(path.join(cache_location, '{}.npy'.format(nd_arr_field)))
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

        return {**ndarrays, **from_data}

    def cache(self, file: File, data: SPT) -> bool | None:
        cache_location = self.cache_location(file)
        if not path.exists(cache_location):
            try:
                makedirs(cache_location)
            except Exception as e:
                print(e)
                self.raise_permission_error('create necessary caching directories')
        data_file = self.data_file(file)
        from_data: NestedBaseVals = {}

        try:
            for key, value in data.items():
                if isinstance(value, ndarray):
                    np.save(
                        path.join(cache_location, '{}.npy'.format(key)),
                        value,
                    )
                else:
                    from_data[key] = value

            if len(from_data.keys()) > 0:
                with open(data_file, 'w') as df:
                    json.dump(from_data, df, check_circular=False, cls=NpEncoder)

            if self.cache_plots:
                pass
        except Exception as e:
            print(e)
            try:
                rmtree(cache_location)
            finally:
                return False
        return True

    def process(self, file: File) -> SPT:
        with SoundFile.from_file(file) as sound:
            return sound.features()

    # Override method to accommodate for plot caching
    def features(self, file: File) -> SPT:
        data: SPT = super().features(file)

        if self.cache_plots and not self.are_plots_cached(file):
            self.cache_plot_files(file, data)

        return data


def plot_and_save(data, sr, file_path):
    # TODO handle different types of plots
    fig, ax = plt.subplots()
    librosa.display.specshow(
        data,
        sr=sr,
        ax=ax
    )
    plt.savefig(file_path)

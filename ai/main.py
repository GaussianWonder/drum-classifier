#!./venv/bin/python3.10

import fire  # type: ignore
import time

from files.file import File
# from files.handler import DatasetFileHandler
# from files.handler.labelling_strategies import most_significant_label
# from files.handler.file_mappings import path_to_file
from files.processor.sound_processor import SoundProcessor
# from files.sound import SoundFile


class Main(object):
    def process(self, file_path: str, out_dir: str = './process', discard: bool = False):
        """Extract features of this audio file for caching purposes

        :param file_path: path to audio file
        :param out_dir: serialized tensors and json files
        :param discard: should discard (delete) the input file after processing
        :returns: prints a json containing paths and information related to all exported files
        """
        pass

    def classify(self, file_path: str, model_identifier: str):
        """Using one of the requested trained models classify the given audio file

        :param file_path: path to audio file
        :param model_identifier: identifier for the model to be used in the classification process
        :returns: prints a json containing relevant information
        """
        pass

    def train(self, assets_path: str = './assets', test_assets_path: str = './test_assets'):
        """Given asset paths train a model and print training stats

        :param assets_path: path to assets split into categories
        :param test_assets_path: path to other assets, split into categories, only to be used for stats (10% * assets)
        :returns: prints a json containing relevant information
        """
        pass

    def list(self):
        """List all trained models

        :returns: prints a json containing an array of model identifiers
        """
        pass


if __name__ == '__main__':
    print('Boot!')

    # fire.Fire(Main)

    # processor = SoundProcessor.init('./temp', cache_plots=True)
    # file = File('./temp/weird.mp3')
    #
    # no_cache_t = time.perf_counter()
    # features = processor.features(file)
    # no_cache_t_end = time.perf_counter()
    # no_cache_t_elapse = no_cache_t_end - no_cache_t
    #
    # cache_t = time.perf_counter()
    # cached_features = processor.features(file)
    # cache_t_end = time.perf_counter()
    # cache_t_elapse = time.perf_counter() - cache_t
    #
    # print('Uncached {}s\nCached {}s'.format(no_cache_t_elapse, cache_t_elapse))
    # print(features)
    # print(cached_features)

    # with SoundFile.from_path('./temp/weird.mp3') as sound:
    #     print(sound.identity)

    # handler: DatasetFileHandler[str, File, dict[str, ndarray]] = DatasetFileHandler[str, File, dict[str, ndarray]].from_cwd(
    #     label_strategy=most_significant_label,
    #     file_map=path_to_file,
    #     file_processor=SoundProcessor.init('./temp')
    # )
    # for asd in handler.get_files():
    #     pass

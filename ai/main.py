#!./venv/bin/python3.10

import fire  # type: ignore

from files.file import File
from files.handler import DatasetFileHandler
from files.handler.labelling_strategies import most_significant_label
from files.handler.file_mappings import path_to_file
from files.processor.sound_processor import SoundProcessor


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
    fire.Fire(Main)

    # handler: DatasetFileHandler[str, File, dict] = DatasetFileHandler[str, File, dict].from_cwd(
    #     label_strategy=most_significant_label,
    #     file_map=path_to_file,
    #     file_processor=SoundProcessor.init('./temp')
    # )
    # for asd in handler.get_files():
    #     pass

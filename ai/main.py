#!./venv/bin/python3.10

import fire  # type: ignore

from files.file import File
from files.handler.sound_handler import sound_handler
from files.processor.sound_processor import SoundProcessor
from files.processor.utils import split_by_transients_if_applicable, transients, plot_transients
from files.sound import SoundFile


class Main(object):
    @staticmethod
    def cache(assets: str = './assets', cache: str = './cached', plots: bool = False):
        """Given an asset folder, a caching directory and the option to generate plots, cache everything

        :param assets: the assets path
        :param cache: the caching directory
        :param plots: consider generating plots or not
        :returns: nothing. all data can be traced back from the cache directory
        """
        sound_handler(assets=assets, cache=cache, plots=plots).cache_all()

    @staticmethod
    def process(file_path: str, cache_dir: str = './cached', plots: bool = False, discard: bool = False):
        """Extract features of this audio file for caching purposes

        :param file_path: path to audio file
        :param cache_dir: cashed results will get here, inside a unique folder named `<file_identity>`
        :param plots: consider generating plots or not
        :param discard: should discard (delete) the input file after processing
        :returns: prints the identity of the file, such that results can be traced to `cache_dir/file_identity`
        """
        file = File(file_path)
        SoundProcessor.init(cache_dir=cache_dir, cache_plots=plots).process(file)

        if discard:
            file.delete()

        print(file.identity)

    @staticmethod
    def classify(file_path: str, model_identifier: str):
        """Using one of the requested trained models classify the given audio file

        :param file_path: path to audio file
        :param model_identifier: identifier for the model to be used in the classification process
        :returns: prints a json containing relevant information
        """
        pass

    @staticmethod
    def train(assets_path: str = './assets', cache_dir: str = './cached', test_assets_path: str = './test_assets'):
        """Given asset paths train a model and directories which optionally contain cached data, print training stats

        :param assets_path: path to assets split into categories
        :param cache_dir: path to directory which can contain cached data
        :param test_assets_path: path to other assets, only to be used for stats (10% * assets)
        :returns: prints a json containing relevant information
        """
        # TODO remove test_assets_path, and make this split programmatically (and random for that matter)
        pass

    @staticmethod
    def list():
        """List all trained models

        :returns: prints a json containing an array of model identifiers
        """
        pass


if __name__ == '__main__':
    # fire.Fire(Main)
    # /home/virghi/Documents/facultate/licenta/project/ai/temp/4hits_no_last_click/4hits_no_last_click_2.wav

    # with SoundFile.from_path('/home/virghi/Documents/facultate/licenta/project/ai/temp/4hits_no_last_click/4hits_no_last_click_2.wav') as sound:
    #     print(len(sound.samples), sound.duration)

    with SoundFile.from_path('./temp/multi_real_kick_drum.wav') as sound:
        pass
        #     files = split_by_transients_if_applicable(
        #         sound=sound,
        #         new_folder=True,
        #         remove_original_if_split=False,
        #     )
        #     print(len(files))

        # energy, raw_onsets, backtracked_onsets = transients(
        #     y=sound.samples,
        #     sr=sound.sample_rate,
        # )
        # plot_transients(energy, raw_onsets, backtracked_onsets)

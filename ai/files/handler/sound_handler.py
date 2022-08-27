from files.file import File
from files.handler import DatasetFileHandler
from files.handler.file_mappings import path_to_file
from files.handler.labelling_strategies import most_significant_label
from files.processor.sound_processor import SoundProcessor
from files.processor.typings import SPT
from files.processor.utils import split_by_transients_if_applicable, applicable_for_transient_split

from files.sound import SoundFile


class SoundFileHandler(DatasetFileHandler[str, File, SPT]):
    def split_transients(self):
        for _, p, _ in self.get_paths():
            if applicable_for_transient_split(file_path=p):
                with SoundFile.from_path(path=p) as sound:
                    split_by_transients_if_applicable(
                        sound=sound,
                        new_folder=True,
                        remove_original_if_split=True,
                    )


def sound_handler(assets: str, cache: str, plots: bool) -> SoundFileHandler:
    return SoundFileHandler.for_folder(
        folder=assets,
        label_strategy=most_significant_label,
        file_map=path_to_file,
        file_processor=SoundProcessor.init(
            cache_dir=cache,
            cache_plots=plots,
        )
    )

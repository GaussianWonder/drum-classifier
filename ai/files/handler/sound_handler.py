from files.file import File
from files.handler import DatasetFileHandler
from files.handler.file_mappings import path_to_file
from files.handler.labelling_strategies import most_significant_label
from files.processor.sound_processor import SoundProcessor
from files.processor.typings import SPT


def sound_handler(assets: str, cache: str, plots: bool) -> DatasetFileHandler[str, File, SPT]:
    return DatasetFileHandler[str, File, SPT].for_folder(
        folder=assets,
        label_strategy=most_significant_label,
        file_map=path_to_file,
        file_processor=SoundProcessor.init(
            cache_dir=cache,
            cache_plots=plots,
        )
    )

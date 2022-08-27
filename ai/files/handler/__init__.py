from glob import glob
from os import path, getcwd, listdir
from typing import Type, TypeVar, Generic, Callable

from files.processor import DatasetItemProcessor

# Self type (DatasetFileHandler)
SelfDFH = TypeVar("SelfDFH", bound="DatasetFileHandler")
# The label type returned by the labelling strategy
LabelT = TypeVar("LabelT")
# The File type that paths are mapped to
FileT = TypeVar("FileT")
# The data type that the processing unit yields
T = TypeVar("T")


# TODO: get_paths and get_paths_per_category should be optional stripped from this file
# ie: other ways of fetching file paths exist (from serialized documents / http requests)
# this specific implementation of finding files should be stripped away (like labelling strategies and file mappings)


class DatasetFileHandler(Generic[LabelT, FileT, T]):
    # Type ignores exist mostly because mypy does not support alias for a generic type bound to some typevars
    base_path: str = getcwd()
    categories: list[str]

    label_strategy: Callable[[str, str], LabelT]
    file_map: Callable[[str], FileT]
    file_processor: Type[DatasetItemProcessor[FileT, T]]

    def __init__(
            self: SelfDFH,
            base_path: str,
            label_strategy: Callable[[str, str], LabelT],
            file_map: Callable[[str], FileT],
            file_processor: Type[DatasetItemProcessor[FileT, T]],
    ):
        if not path.exists(base_path) or not path.isdir(base_path):
            raise Exception('Folder {} does not exist!'.format(base_path))

        self.label_strategy = label_strategy  # type: ignore
        self.file_map = file_map  # type: ignore
        self.file_processor = file_processor

        self.base_path = base_path
        self.categories = self.get_categories()
        self.categories.sort()  # for compatibility check

    @classmethod
    def from_cwd(
            cls,
            label_strategy: Callable[[str, str], LabelT],
            file_map: Callable[[str], FileT],
            file_processor: Type[DatasetItemProcessor[FileT, T]],
    ):
        return cls(getcwd(), label_strategy, file_map, file_processor)

    @classmethod
    def for_folder(
            cls,
            folder: str | None,
            label_strategy: Callable[[str, str], LabelT],
            file_map: Callable[[str], FileT],
            file_processor: Type[DatasetItemProcessor[FileT, T]],
    ):
        if folder is None:
            return cls.from_cwd(label_strategy, file_map, file_processor)
        return cls(folder, label_strategy, file_map, file_processor)

    def cache_all(self):
        for _, files in self.get_files_per_category():
            for file, _ in files:
                if not self.file_processor.is_cached(file):  # type: ignore
                    self.file_processor.features(file)  # type: ignore

    def get_categories(self) -> list[str]:
        return get_asset_categories(self.base_path)

    def get_paths(self) -> list[tuple[str, str, LabelT]]:
        """Get all paths with associated category and LabelT

        :return: A huge list of (category, FileT, LabelT)
        """
        return [
            (category, p, self.label_strategy(p, self.base_path))  # type: ignore
            for (category, p) in get_files(self.base_path, self.categories)
        ]

    def get_files(self) -> list[tuple[str, FileT, LabelT]]:
        """Get all FileT with associated category and LabelT

        :return: A huge list of (category, FileT, LabelT)
        """
        return [
            (category, self.file_map(p), self.label_strategy(p, self.base_path))  # type: ignore
            for (category, p) in get_files(self.base_path, self.categories)
        ]

    def get_paths_per_category(self) -> list[tuple[str, list[tuple[str, LabelT]]]]:
        """Convert paths to tuples (path, LabelT) provided by the labelling strategy and file mapper

        :return: List of paths with associated labels grouped by category
        """
        return [
            (
                category,
                [(p, self.label_strategy(p, self.base_path)) for p in paths]  # type: ignore
            )
            for (category, paths) in get_paths(self.base_path, self.categories)
        ]

    def get_files_per_category(self) -> list[tuple[str, list[tuple[FileT, LabelT]]]]:
        """Convert paths to tuples (FileT, LabelT) provided by the labelling strategy and file mapper

        :return: List of SoundFiles with associated labels grouped by category
        """
        return [
            (
                category,
                [(self.file_map(p), self.label_strategy(p, self.base_path)) for p in paths]  # type: ignore
            )
            for (category, paths) in get_paths(self.base_path, self.categories)
        ]

    def is_compatible_with(self: SelfDFH, other: SelfDFH) -> bool:
        return self.categories == other.categories


def get_asset_categories(asset_path: str) -> list[str]:
    categories = []
    for f_name in listdir(asset_path):
        maybe_dir = path.join(asset_path, f_name)
        if path.isdir(maybe_dir):
            categories.append(f_name)
    return categories


def category_patterns(category: str, asset_path: str):
    return (
        '{assets}/{category}/**/*.wav'.format(category=category, assets=asset_path),
        '{assets}/{category}/**/*.WAV'.format(category=category, assets=asset_path),
        '{assets}/{category}/**/*.mp3'.format(category=category, assets=asset_path),
        '{assets}/{category}/**/*.MP3'.format(category=category, assets=asset_path),
        '{assets}/{category}/**/*.ogg'.format(category=category, assets=asset_path),
    )


def patterns_to_paths(patterns):
    return [
        p_path
        for pattern in patterns
        for p_path in glob(pattern, recursive=True)
    ]


def get_patterns(asset_path: str, categories: list[str]):
    return [
        (category, category_patterns(category, asset_path))
        for category in categories
    ]


def get_paths(asset_path: str, categories: list[str]) -> list[tuple[str, list[str]]]:
    return [
        (category, patterns_to_paths(patterns))
        for (category, patterns) in get_patterns(asset_path, categories)
    ]


def get_files(asset_path: str, categories: list[str]):
    return [
        (category, file_path)
        for (category, paths) in get_paths(asset_path, categories)
        for file_path in paths
    ]

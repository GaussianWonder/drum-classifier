from glob import glob
from os import path, getcwd, listdir
from typing import Generic, TypeVar, Callable

# Self type (DatasetFileHandler)
from files.sound import SoundFile
from files.handler.labelling_strategies import most_significant_label

SelfDFH = TypeVar("SelfDFH", bound="DatasetFileHandler")
# The label type returned by the labelling strategy
LabelT = TypeVar("LabelT")
# Labelling strategy function type: (FilePath, AssetPath -> LabelType)
LabelStrategyT = Callable[[str, str], LabelT]


class DatasetFileHandler(Generic[LabelT]):
    base_path: str = getcwd()
    label_strategy: LabelStrategyT
    categories: list[str]

    def __init__(self: SelfDFH, base_path: str, label_strategy: LabelStrategyT):
        if not path.exists(base_path) or not path.isdir(base_path):
            raise Exception('Folder {} does not exist!'.format(base_path))
        self.label_strategy = label_strategy
        self.base_path = base_path
        self.categories = self.get_categories()
        self.categories.sort()

    @classmethod
    def from_cwd(cls, label_strategy: Callable[[str, str], LabelT] = most_significant_label):
        return cls(getcwd(), label_strategy)

    @classmethod
    def for_folder(cls, folder: str | None = None, label_strategy: LabelStrategyT = most_significant_label):
        if folder is None:
            return cls.from_cwd(label_strategy)
        return cls(folder, label_strategy)

    def get_categories(self) -> list[str]:
        return get_asset_categories(self.base_path)

    def get_files(self) -> list[tuple[str, str, LabelT]]:
        """Get all paths with associated category and labels

        :return: A huge list of (category, sound_path, labels)
        """
        return [
            (category, p, self.label_strategy(p, self.base_path))
            for (category, p) in get_files(self.base_path, self.categories)
        ]

    def get_sounds(self) -> list[tuple[str, SoundFile, LabelT]]:
        """Get all SoundFiles with associated category and labels

        :return: A huge list of (category, sound, labels)
        """
        return [
            (category, SoundFile(p), self.label_strategy(p, self.base_path))
            for (category, p) in get_files(self.base_path, self.categories)
        ]

    def get_files_per_category(self) -> list[tuple[str, list[tuple[str, LabelT]]]]:
        """Convert paths to tuples (path, labels) provided by the labelling strategy

        :return: List of paths with associated labels grouped by category
        """
        return [
            (
                category,
                [(p, self.label_strategy(p, self.base_path)) for p in paths]
            )
            for (category, paths) in get_paths(self.base_path, self.categories)
        ]

    def get_sounds_per_category(self):
        """Convert paths to tuples (SoundFile, labels) provided by the labelling strategy

        :return: List of SoundFiles with associated labels grouped by category
        """
        return [
            (
                category,
                [(SoundFile.from_path(p), self.label_strategy(p, self.base_path)) for p in paths]
            )
            for (category, paths) in get_paths(self.base_path, self.categories)
        ]

    def is_compatible_with(self: SelfDFH, other: SelfDFH) -> bool:
        try:
            return self.categories == other.categories
        finally:
            return False


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

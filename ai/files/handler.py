from glob import glob
from os import path, getcwd, listdir
from typing import TypeVar

SelfDFH = TypeVar("SelfDFH", bound="DatasetFileHandler")


class DatasetFileHandler:
    base_path: str = getcwd()
    categories: list[str]

    def __init__(self: SelfDFH, base_path: str):
        if not path.exists(base_path) or not path.isdir(base_path):
            raise Exception('Folder {} does not exist!'.format(base_path))
        self.base_path = base_path
        self.categories = self.get_categories()
        self.categories.sort()

    @classmethod
    def from_cwd(cls):
        return cls(getcwd())

    @classmethod
    def for_folder(cls, folder: str | None = None):
        if folder is None:
            return cls.from_cwd()
        return cls(folder)

    def get_categories(self) -> list[str]:
        return get_asset_categories(self.base_path)

    def get_patterns(self):
        return get_patterns(self.base_path, self.categories)

    def get_files(self):
        return get_files(self.base_path, self.categories)

    def get_files_per_category(self):
        return get_paths(self.base_path, self.categories)

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


def get_paths(asset_path: str, categories: list[str]) -> list[tuple[str, list[str | bytes]]]:
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

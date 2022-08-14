from os import path


def path_label_list(file_path: str, assets_path: str) -> list[str]:
    """For a given file and assets path, extract all relevant labels. By design, labels path oriented.

    :param file_path: Path to file
    :param assets_path: Path to asset directory
    :return: All nested labels extracted from 'path' after the asset path
    """
    relpath = path.relpath(file_path, assets_path)
    return path.dirname(relpath).split('/')


def most_significant_and_secondaries(file_path: str, assets_path: str) -> tuple[str, list[str]]:
    labels = path_label_list(file_path, assets_path)
    return labels[0], labels[1:]


def most_significant_label(file_path: str, asset_path: str) -> str:
    return path_label_list(file_path, asset_path)[0]

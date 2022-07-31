from files.handler import DatasetFileHandler

if __name__ == '__main__':
    file_handler = DatasetFileHandler.for_folder('./assets')
    for (category, paths) in file_handler.get_files_per_category():
        print(category, len(paths))

    test_fh = DatasetFileHandler.for_folder('./test_assets')
    print(file_handler.is_compatible_with(test_fh))

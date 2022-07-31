from os import path as opath

import librosa

from files.file import File
from numpy import number, ndarray


class SoundFile(File):
    # soundfile data
    samples: ndarray = []
    sample_rate: number = None

    # Relevant info
    duration: number = None

    def __init__(self, path: str):
        super().__init__(path)

    @classmethod
    def from_path(cls, path: str):
        return cls(path)

    @classmethod
    def from_file(cls, file: File):
        return cls(file.path)

    def get_path_labels(self) -> (str, str, list[str]):
        # TODO make up a category plan when working with the dataset
        # TODO check this and strip out details that are not relevant,
        #   categories that are too complex mess up the training process
        relpath = opath.relpath(self.path, "./assets")
        labels = opath.dirname(relpath).split('/')
        return labels[0], labels[-1], labels[1:-1]

    def load_sound(self):
        """Load the audio file and set relevant information

        :return: None
        """
        samples, sample_rate = librosa.load(self.path)
        self.samples = samples
        self.sample_rate = sample_rate
        self.duration = float(len(samples)) / sample_rate

    def is_loaded(self):
        """ Check if the SoundFile instance has loaded the audio file itself. This yields true when using `with _ as _`

        :return: bool
        """
        return not(self.duration is None or self.sample_rate is None or not self.samples or not len(self.samples) == 0)

    def __enter__(self):
        self.load_sound()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None or exception_type is not None:
            print("Error thrown when dealing with a SoundFile")
            print(exception_type)
            print(exception_value)
            print(exception_traceback)
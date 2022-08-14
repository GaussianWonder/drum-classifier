import librosa  # type: ignore

import preferences
from files.file import File
from numpy import number, ndarray


class SoundFile(File):
    # soundfile data
    samples: ndarray
    sample_rate: int = 0

    # Relevant info
    duration: int = 0

    def __init__(self, path: str):
        super().__init__(path)

    @classmethod
    def from_path(cls, path: str):
        return cls(path)

    @classmethod
    def from_file(cls, file: File):
        return cls(file.path)

    def load_sound(self):
        """Load the audio file and set relevant information

        :return: None
        """
        samples, sample_rate, duration = preferences.load_sound(self.path)
        self.samples = samples
        self.sample_rate = sample_rate
        self.duration = duration

    def is_loaded(self):
        """ Check if the SoundFile instance has loaded the audio file itself. This yields true when using `with _ as _`

        :return: bool
        """
        return not(self.duration is 0 or self.sample_rate is 0 or not hasattr(self, 'samples'))

    def __enter__(self):
        self.load_sound()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None or exception_type is not None:
            print("Error thrown when dealing with a SoundFile")
            print(exception_type)
            print(exception_value)
            print(exception_traceback)

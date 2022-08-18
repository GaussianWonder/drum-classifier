import librosa  # type: ignore
import numpy as np

import preferences
from files.file import File
from numpy import ndarray

from files.processor.typings import SPT


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
        return not(self.duration <= 0 or self.sample_rate <= 0 or not hasattr(self, 'samples'))

    def features(self) -> SPT:
        stft: ndarray = np.abs(librosa.stft(self.samples))

        mfcc: ndarray = librosa.feature.mfcc(
            y=self.samples,
            sr=self.sample_rate,
            n_mfcc=preferences.N_MFCC,
        )

        chroma: ndarray = librosa.feature.chroma_stft(
            S=stft,
            sr=self.sample_rate,
        )
        chroma_cens: ndarray = librosa.feature.chroma_cens(
            y=self.samples,
            sr=self.sample_rate
        )

        mel: ndarray = librosa.feature.melspectrogram(
            y=self.samples,
            sr=self.sample_rate,
        )

        contrast: ndarray = librosa.feature.spectral_contrast(
            S=stft,
            sr=self.sample_rate,
        )
        spectral_bandwidth: ndarray = librosa.feature.spectral_bandwidth(
            y=self.samples,
            sr=self.sample_rate,
        )

        tonnetz: ndarray = librosa.feature.tonnetz(
            y=librosa.effects.harmonic(self.samples),
            sr=self.sample_rate,
        )

        return {
            'info': {
                'sample_rate': self.sample_rate,
                'duration': self.duration,
                'name': self.name,
                'ext': self.ext,
                'path': self.path,
            },
            'stft': stft,
            'mfcc': mfcc,
            'chroma': chroma,
            'chroma_cens': chroma_cens,
            'mel': mel,
            'contrast': contrast,
            'spectral_bandwidth': spectral_bandwidth,
            'tonnetz': tonnetz,
        }

    def __enter__(self):
        self.load_sound()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None or exception_type is not None:
            print("Error thrown when dealing with a SoundFile")
            print(exception_type)
            print(exception_value)
            print(exception_traceback)

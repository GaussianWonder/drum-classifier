# TODO handle audio files that do not start with a sharp transient straight away (delayed sample)
import librosa  # type: ignore
import librosa.util  # type: ignore
from numpy import ndarray

# CONSTANTS
CONVERT_TO_MONO = True
MAX_DURATION = 2  # in seconds

N_MFCC = 20

SAMPLE_RATE = 44100

# DEFAULT IMPLEMENTATIONS


def load_sound(file_path: str) -> tuple[ndarray, int, int]:
    """A uniform way to load and start processing sounds. Fixed sample_rate, fixed length,

    :param file_path: Path to the desired file to load
    :return: [samples, sample_rate, sound duration]
    """
    samples, sample_rate = librosa.load(
        file_path,
        sr=SAMPLE_RATE,
        mono=CONVERT_TO_MONO,
        duration=MAX_DURATION,
    )
    return librosa.util.normalize(samples), sample_rate, float(len(samples)) / sample_rate

# TODO handle audio files that do not start with a sharp transient straight away (delayed sample)
import librosa  # type: ignore
import librosa.util  # type: ignore
from librosa.effects import trim  # type: ignore
from numpy import ndarray

# CONSTANTS
SAMPLE_RATE = 44100
CONVERT_TO_MONO = True
MAX_DURATION = 1.5
MIN_DURATION = 0.01
SILENCE_DB = 60

FADE_IN_DURATION = 0.005
FADE_OUT_DURATION = 0.01

N_MFCC = 20

# DEFAULT IMPLEMENTATIONS


def load_sound(file_path: str) -> tuple[ndarray, int, float]:
    """A uniform way to load and start processing sounds. Fixed sample_rate, fixed length,

    :param file_path: Path to the desired file to load
    :return: [samples, sample_rate, sound duration]
    """
    samples, sample_rate = librosa.load(
        file_path,
        sr=SAMPLE_RATE,
        mono=CONVERT_TO_MONO,
    )
    (trimmed_silence, _) = trim(
        y=samples,
        top_db=SILENCE_DB,
    )

    return librosa.util.normalize(trimmed_silence), sample_rate, librosa.get_duration(y=trimmed_silence, sr=sample_rate)

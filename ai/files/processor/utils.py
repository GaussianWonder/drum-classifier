import librosa  # type: ignore
import librosa.display  # type: ignore
import librosa.util  # type: ignore
import librosa.onset  # type: ignore
from soundfile import write as write_sound  # type: ignore
from matplotlib import pyplot as plt  # type: ignore

import numpy as np
from numpy import ndarray

from os import path, makedirs

from files.file import File
from files.sound import SoundFile
import preferences


def sample_len(sr: int | None = None, duration: float = 0.005, samples: int | None = None) -> int:
    """Calculate the desired sample length and throw runtime errors when sample count cannot be calculated.

    :param samples: if provided, duration and sr will be ignored
    :param sr: sample rate, only needed when duration is provided
    :param duration: sample length will be calculated from sr and duration
    :return: sample length, either the provided samples, or a calculation based on duration and sampling rate
    """

    if samples is None:
        if sr is None:
            raise Exception('Sampling rate is needed when calculating sample count from duration in seconds.')
        return int(duration * sr)
    else:
        return samples


def fadein(
        y: ndarray,
        samples: int | None = None,
        sr: int | None = None,
        duration: float = 0.005,
        curve_function=np.linspace,
):
    """ Applies a fadein to the first samples

    :param y: audio time series to fade in
    :param samples: the amount of samples used for the fadein
    :param sr: sampling rate. optional, if duration samples is not provided
    :param duration: duration of the fadein. ignored if samples is provided.
    :param curve_function: The curve generation function. Choose from linspace, geomspace, logspace
    :return: audio time series faded in with the desired fadein curve
    """
    length = sample_len(sr=sr, duration=duration, samples=samples)

    start = 0
    end = length

    y[start:end] = y[start:end] * curve_function(0.0, 1.0, length)


def fadeout(
        y: ndarray,
        samples: int | None = None,
        sr: int | None = None,
        duration: float = 0.005,
        curve_function=np.linspace,
):
    """ Applies a fadeout the last samples

    :param y: audio time series to fade in
    :param samples: the amount of samples used for the fadein
    :param sr: sampling rate. optional, if duration samples is not provided
    :param duration: duration of the fadein. ignored if samples is provided.
    :param curve_function: The curve generation function. Choose from linspace, geomspace, logspace
    :return: audio time series faded in with the desired fadein curve
    """
    length = sample_len(sr=sr, duration=duration, samples=samples)

    end = y.shape[0]
    start = end - length

    y[start:end] = y[start:end] * curve_function(1.0, 0.0, length)


def fade_edges(
        fadein_duration: float = 0.005,
        fadeout_duration: float = 0.005,
        **kwargs,
):
    """Apply a fadein and a fadeout to a given audio time series. Fade type will be identical for both ends.

    :param fadein_duration: custom fadein duration
    :param fadeout_duration: custom fadeout duration
    :param kwargs: Args for fadein and fadeout are identical. See fadein and fadeout functions.
    """
    fadein(
        **kwargs,
        duration=fadein_duration,
    )
    fadeout(
        **kwargs,
        duration=fadeout_duration,
    )


def transients(
        y: ndarray,
        sr: int,
        onset_strength: ndarray | None = None,
        normalize: bool = True,
) -> tuple[ndarray, ndarray, ndarray]:
    onset_strength_env = onset_strength if onset_strength is not None else librosa.onset.onset_strength(
        y=y,
        sr=sr,
    )
    onsets = librosa.onset.onset_detect(
        onset_envelope=onset_strength_env,
        normalize=normalize,
        # delta=float,
        # wait=int,
    )
    backtracked_onsets = librosa.onset.onset_backtrack(
        events=onsets,
        energy=onset_strength_env,
    )
    return onset_strength_env, onsets, backtracked_onsets


def plot_transients(energy: ndarray, onsets: ndarray, backtracked_onsets: ndarray, save_file: str | None = None):
    _, _ = plt.subplots(nrows=1, sharex=True)  # type: ignore
    times = librosa.times_like(energy)

    plt.plot(times, energy, label='Onset strength', color='b', alpha=.5)
    plt.vlines(
        librosa.frames_to_time(onsets),
        0, energy.max(initial=-1000),
        label='Raw onsets',
        color='g',
    )
    plt.vlines(
        librosa.frames_to_time(backtracked_onsets),
        0, energy.max(initial=-1000),
        label='Backtracked',
        color='r'
    )
    plt.legend()

    if save_file is not None:
        plt.savefig(save_file)
    else:
        plt.show()


def split_by_transients(
        sound: SoundFile,
        onset_strength: ndarray | None = None,
        normalize: bool = True,
        new_folder: bool = False,
) -> list[File]:
    # Choose a save location
    save_basedir = path.dirname(sound.path)
    if new_folder:
        save_basedir = path.join(save_basedir, sound.name)
        if not path.exists(save_basedir):
            makedirs(save_basedir)

    # Compute transients
    (_, _, backtracked_onsets) = transients(
        y=sound.samples,
        sr=sound.sample_rate,
        onset_strength=onset_strength,
        normalize=normalize,
    )

    # Get sample indexes of each onset frame
    new_paths: list[str] = []
    sample_indexes = np.concatenate(
        librosa.frames_to_samples(backtracked_onsets),
        len(sound.samples),
    )
    index_count = len(sample_indexes)
    last_addressable = index_count - 1
    i = 1
    while i < last_addressable:
        # foreach onset frame, make a new audio file until the next onset frame
        start = sample_indexes[i - 1]
        end = sample_indexes[i]

        audio = sound.samples[start:end]
        audio_path = path.join(
            save_basedir,
            '{}_{}{}'.format(sound.name, i, sound.ext)
        )

        if librosa.get_duration(y=audio, sr=sound.sample_rate) > preferences.MAX_DURATION:
            # Fix the duration of the audio file only if larger than the max accepted duration
            audio = librosa.util.fix_length(
                data=audio,
                size=sample_len(
                    sr=sound.sample_rate,
                    duration=preferences.MAX_DURATION
                ),
            )

        fade_edges(
            y=audio,
            sr=sound.sample_rate,
            fadein_duration=0.005,
            fadeout_duration=0.01,
        )

        write_sound(audio_path, audio, sound.sample_rate)
        new_paths.append(audio_path)

        i += 1

    return [File(p) for p in new_paths]


def split_by_transients_if_applicable(
        sound: SoundFile,
        onset_strength: ndarray | None = None,
        normalize: bool = True,
        remove_original_if_split: bool = True,
        new_folder: bool = False,
) -> list[File]:
    if sound.duration < preferences.MAX_DURATION:
        return [sound]

    if remove_original_if_split:
        # The soundfile can be deleted already, since data related to this file is still available
        sound.delete()

    return split_by_transients(
        sound=sound,
        onset_strength=onset_strength,
        normalize=normalize,
        new_folder=new_folder,
    )

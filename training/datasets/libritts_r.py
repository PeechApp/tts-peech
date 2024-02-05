import os
import pandas as pd

from pathlib import Path
from typing import Tuple, Union

import torchaudio
from torch import Tensor
from torch.utils.data import Dataset
from torchaudio._internal import download_url_to_file # type: ignore
from torchaudio.datasets.utils import _extract_tar


URL = "train-clean-100"
FOLDER_IN_ARCHIVE = "LibriTTS"
_CHECKSUMS = {
    "http://us.openslr.org/resources/141/dev_clean.tar.gz": "2c1f5312914890634cc2d15783032ff3",  # noqa: E501
    "http://us.openslr.org/resources/141/dev_other.tar.gz": "62d3a80ad8a282b6f31b3904f0507e4f",  # noqa: E501
    "http://us.openslr.org/resources/141/test_clean.tar.gz": "4d373d453eb96c0691e598061bbafab7",  # noqa: E501
    "http://us.openslr.org/resources/141/test_other.tar.gz": "dbc0959d8bdb6d52200595cabc9995ae",  # noqa: E501
    "http://us.openslr.org/resources/141/train_clean_100.tar.gz": "6df668d8f5f33e70876bfa33862ad02b",  # noqa: E501
    "http://us.openslr.org/resources/141/train_clean_360.tar.gz": "382eb3e64394b3da6a559f864339b22c",  # noqa: E501
    "http://us.openslr.org/resources/141/train_other_500.tar.gz": "a37a8e9f4fe79d20601639bf23d1add8",  # noqa: E501
}


def load_libritts_item(
    fileid: str,
    path: str,
    ext_audio: str,
    ext_original_txt: str,
    ext_normalized_txt: str,
) -> Tuple[Tensor, int, str, str, int, int, str]:
    speaker_id, chapter_id, segment_id, utterance_id = fileid.split("_")
    utterance_id = fileid

    file_audio = utterance_id + ext_audio
    file_audio = os.path.join(path, speaker_id, chapter_id, file_audio)

    # Load audio
    waveform, sample_rate = torchaudio.load(file_audio) # type: ignore

    # Try to load transcriptions from individual files
    normalized_text_filename = utterance_id + ext_normalized_txt
    normalized_text_path = os.path.join(path, speaker_id, chapter_id, normalized_text_filename)

    original_text_filename = utterance_id + ext_original_txt
    original_text_path = os.path.join(path, speaker_id, chapter_id, original_text_filename)

    try:
        # Load normalized text
        with open(normalized_text_path, "r") as ft:
            normalized_text = ft.readline()

        # Load original text
        with open(original_text_path) as ft:
            original_text = ft.readline()

    except FileNotFoundError:
        # If individual files are not found, load from .tsv file
        trans_file = f"{speaker_id}_{chapter_id}.trans.tsv"
        trans_file = os.path.join(path, speaker_id, chapter_id, trans_file)
        df = pd.read_csv(trans_file, sep='\t', header=None, names=['id', 'original_text', 'normalized_text'])

        row = df[df['id'] == utterance_id].iloc[0]

        original_text = row['original_text']
        normalized_text = row['normalized_text']

        # Save original_text and normalized_text to separate text files
        with open(normalized_text_path, 'w') as ft:
            ft.write(original_text)

        with open(original_text_path, 'w') as ft:
            ft.write(normalized_text)

    return (
        waveform,
        sample_rate,
        original_text,
        normalized_text,
        int(speaker_id),
        int(chapter_id),
        utterance_id,
    )


class LIBRITTS_R(Dataset):
    """ "*LibriTTS-R*: A Restored Multi-Speaker Text-to-Speech Corpus," arXiv, 2023

    Args:
        root (str or Path): Path to the directory where the dataset is found or downloaded.
        url (str, optional): The URL to download the dataset from,
            or the type of the dataset to dowload.
            Allowed type values are ``"dev-clean"``, ``"dev-other"``, ``"test-clean"``,
            ``"test-other"``, ``"train-clean-100"``, ``"train-clean-360"`` and
            ``"train-other-500"``. (default: ``"train-clean-100"``)
        folder_in_archive (str, optional):
            The top-level directory of the dataset. (default: ``"LibriTTS"``)
        download (bool, optional):
            Whether to download the dataset if it is not found at root path. (default: ``False``).
    """

    _ext_original_txt = ".original.txt"
    _ext_normalized_txt = ".normalized.txt"
    _ext_audio = ".wav"

    def __init__(
        self,
        root: Union[str, Path],
        url: str = URL,
        folder_in_archive: str = FOLDER_IN_ARCHIVE,
        download: bool = False,
    ) -> None:

        if url in [
            "dev-clean",
            "dev-other",
            "test-clean",
            "test-other",
            "train-clean-100",
            "train-clean-360",
            "train-other-500",
        ]:

            ext_archive = ".tar.gz"
            base_url = "http://us.openslr.org/resources/141/"

            url = os.path.join(base_url, url + ext_archive)

        # Get string representation of 'root' in case Path object is passed
        root = os.fspath(root)

        basename = os.path.basename(url)
        archive = os.path.join(root, basename)

        basename = basename.split(".")[0]
        folder_in_archive = os.path.join(folder_in_archive, basename)

        self._path = os.path.join(root, folder_in_archive)

        if download:
            if not os.path.isdir(self._path):
                if not os.path.isfile(archive):
                    checksum = _CHECKSUMS.get(url, None)
                    download_url_to_file(url, archive, hash_prefix=checksum)
                _extract_tar(archive)
        else:
            if not os.path.exists(self._path):
                raise RuntimeError(
                    f"The path {self._path} doesn't exist. "
                    "Please check the ``root`` path or set `download=True` to download it"
                )

        self._walker = sorted(str(p.stem) for p in Path(self._path).glob("*/*/*" + self._ext_audio))

    def __getitem__(self, n: int) -> Tuple[Tensor, int, str, str, int, int, str]:
        """Load the n-th sample from the dataset.

        Args:
            n (int): The index of the sample to be loaded

        Returns:
            Tuple of the following items;

            Tensor:
                Waveform
            int:
                Sample rate
            str:
                Original text
            str:
                Normalized text
            int:
                Speaker ID
            int:
                Chapter ID
            str:
                Utterance ID
        """
        fileid = self._walker[n]
        return load_libritts_item(
            fileid,
            self._path,
            self._ext_audio,
            self._ext_original_txt,
            self._ext_normalized_txt,
        )

    def __len__(self) -> int:
        return len(self._walker)
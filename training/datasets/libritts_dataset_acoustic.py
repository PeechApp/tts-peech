import os
import json
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset

from model.config import lang2id
from training.preprocess import PreprocessLibriTTS
from training.tools import pad_1D, pad_2D, pad_3D

from .libritts_r import LIBRITTS_R


class LibriTTSDatasetAcoustic(Dataset):
    r"""Loading preprocessed acoustic model data."""

    def __init__(
        self,
        lang: str = "en",
        root: str = "datasets_cache/LIBRITTS",
        url: str = "train-clean-360",
        download: bool = True,
        cache: bool = False,
        mem_cache: bool = False,
        cache_dir: str = "datasets_cache",
    ):
        r"""A PyTorch dataset for loading preprocessed acoustic data.

        Args:
            root (str): Path to the directory where the dataset is found or downloaded.
            lang (str): The language of the dataset.
            url (str): The dataset url, default "train-clean-360".
            download (bool, optional): Whether to download the dataset if it is not found. Defaults to True.
            cache (bool, optional): Whether to cache the preprocessed data. Defaults to False.
            cache_dir (str, optional): Path to the directory where the cache is stored. Defaults to "datasets_cache".
        """
        # self.dataset = datasets.LIBRITTS(
        #     root=root,
        #     download=download,
        #     url=url,
        # )
        self.dataset = LIBRITTS_R(
            root=root,
            download=download,
            url=url,
        )
        self.cache = cache

        # Calculate the directory for the cache file
        self.cache_subdir = lambda idx: str(((idx // 1000) + 1) * 1000)

        self.cache_dir = os.path.join(cache_dir, f'cache-{url}')

        self.mem_cache = mem_cache
        self.memory_cache = {}

        # Load the id_mapping dictionary from the JSON file
        with open("speaker_id_mapping_libri.json") as f:
            self.id_mapping = json.load(f)

        self.preprocess_libtts = PreprocessLibriTTS(lang)

    def __len__(self) -> int:
        r"""Returns the number of samples in the dataset.

        Returns
            int: Number of samples in the dataset.
        """
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        r"""Returns a sample from the dataset at the given index.

        Args:
            idx (int): Index of the sample to return.

        Returns:
            Dict[str, Any]: A dictionary containing the sample data.
        """

        # Check if the data is in the memory cache
        if self.mem_cache and idx in self.memory_cache:
            return self.memory_cache[idx]

        # Check if the data is in the cache
        cache_subdir_path = os.path.join(self.cache_dir, self.cache_subdir(idx))
        cache_file = os.path.join(cache_subdir_path, f'{idx}.pt')

        # Check if the data is in the cache
        if self.cache and os.path.exists(cache_file):
            # If the data is in the cache, load it from the cache file and return it
            data = torch.load(cache_file)
            return data

        # Retrive the dataset row
        data = self.dataset[idx]

        data = self.preprocess_libtts.acoustic(data)

        # TODO: bad way to do filtering, fix this!
        if data is None:
            # print("Skipping due to preprocessing error")
            rand_idx = np.random.randint(0, self.__len__())
            return self.__getitem__(rand_idx)

        data.wav = torch.FloatTensor(data.wav.unsqueeze(0))

        result = {
            "id": data.utterance_id,
            "wav": data.wav,
            "mel": data.mel,
            "pitch": data.pitch,
            "text": data.phones,
            "attn_prior": data.attn_prior,
            # "energy": data.energy,
            "raw_text": data.raw_text,
            "normalized_text": data.normalized_text,
            "speaker": self.id_mapping.get(str(data.speaker_id)),
            "pitch_is_normalized": data.pitch_is_normalized,
            # TODO: fix lang!
            "lang": lang2id["en"],
        }

        # Add the data to the memory cache
        if self.mem_cache:
            self.memory_cache[idx] = result

        if self.cache:
            # Create the cache subdirectory if it doesn't exist
            os.makedirs(cache_subdir_path, exist_ok=True)

            # Save the preprocessed data to the cache
            torch.save(result, cache_file)

        return result

    def collate_fn(self, data: List) -> List:
        r"""Collates a batch of data samples.

        Args:
            data (List): A list of data samples.

        Returns:
            List: A list of reprocessed data batches.
        """
        data_size = len(data)

        idxs = list(range(data_size))

        # Initialize empty lists to store extracted values
        empty_lists: List[List] = [[] for _ in range(11)]
        (
            ids,
            speakers,
            texts,
            raw_texts,
            mels,
            pitches,
            attn_priors,
            langs,
            src_lens,
            mel_lens,
            wavs,
            # energy,
        ) = empty_lists

        # Extract fields from data dictionary and populate the lists
        for idx in idxs:
            data_entry = data[idx]
            ids.append(data_entry["id"])
            speakers.append(data_entry["speaker"])
            texts.append(data_entry["text"])
            raw_texts.append(data_entry["raw_text"])
            mels.append(data_entry["mel"])
            pitches.append(data_entry["pitch"])
            attn_priors.append(data_entry["attn_prior"].numpy())
            langs.append(data_entry["lang"])
            src_lens.append(data_entry["text"].shape[0])
            mel_lens.append(data_entry["mel"].shape[1])
            wavs.append(data_entry["wav"].numpy())
            # energy.append(data_entry["energy"].numpy())

        # Convert langs, src_lens, and mel_lens to numpy arrays
        langs = np.array(langs)
        src_lens = np.array(src_lens)
        mel_lens = np.array(mel_lens)

        # NOTE: Instead of the pitches for the whole dataset, used stat for the batch
        # Take only min and max values for pitch
        pitches_stat = list(self.normalize_pitch(pitches)[:2])

        texts = pad_1D(texts)
        mels = pad_2D(mels)
        pitches = pad_1D(pitches)
        attn_priors = pad_3D(attn_priors, len(idxs), max(src_lens), max(mel_lens))

        speakers = np.repeat(
            np.expand_dims(np.array(speakers), axis=1), texts.shape[1], axis=1,
        )
        langs = np.repeat(
            np.expand_dims(np.array(langs), axis=1), texts.shape[1], axis=1,
        )

        wavs = pad_2D(wavs)
        # energy = pad_2D(energy)

        return [
            ids,
            raw_texts,
            torch.from_numpy(speakers),
            torch.from_numpy(texts).int(),
            torch.from_numpy(src_lens),
            torch.from_numpy(mels),
            torch.from_numpy(pitches),
            pitches_stat,
            torch.from_numpy(mel_lens),
            torch.from_numpy(langs),
            torch.from_numpy(attn_priors),
            torch.from_numpy(wavs),
            # torch.from_numpy(energy),
        ]

    def normalize_pitch(
        self, pitches: List[torch.Tensor],
    ) -> Tuple[float, float, float, float]:
        r"""Normalizes the pitch values.

        Args:
            pitches (List[torch.Tensor]): A list of pitch values.

        Returns:
            Tuple: A tuple containing the normalized pitch values.
        """
        pitches_t = torch.concatenate(pitches)

        min_value = torch.min(pitches_t).item()
        max_value = torch.max(pitches_t).item()

        mean = torch.mean(pitches_t).item()
        std = torch.std(pitches_t).item()

        return min_value, max_value, mean, std
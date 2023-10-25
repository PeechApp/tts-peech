import unittest

import torch
from torch.utils.data import DataLoader

from training.datasets.libritts_dataset import LibriTTSDataset


class TestLibriTTSDataset(unittest.TestCase):
    def setUp(self):
        self.batch_size = 2
        self.lang = "en"
        self.sort = False
        self.drop_last = False
        self.download = False

        self.dataset = LibriTTSDataset(
            root="datasets_cache/LIBRITTS",
            batch_size=self.batch_size,
            lang=self.lang,
            sort=self.sort,
            drop_last=self.drop_last,
            download=self.download,
        )

    def test_len(self):
        self.assertEqual(len(self.dataset), 33236)

    def test_getitem(self):
        sample = self.dataset[0]
        self.assertEqual(sample["id"], "1034_121119_000001_000001")
        self.assertEqual(sample["speaker"], 1034)

        self.assertEqual(sample["text"].shape, torch.Size([6]))
        self.assertEqual(sample["mel"].shape, torch.Size([100, 58]))
        self.assertEqual(sample["pitch"].shape, torch.Size([58]))
        self.assertEqual(sample["raw_text"], "The Law.")
        self.assertEqual(sample["normalized_text"], "The Law.")
        self.assertFalse(sample["pitch_is_normalized"])
        self.assertEqual(sample["lang"], 3)
        self.assertEqual(sample["attn_prior"].shape, torch.Size([6, 58]))
        self.assertEqual(sample["wav"].shape, torch.Size([1, 14994]))

    def test_collate_fn(self):
        data = [
            self.dataset[0],
            self.dataset[2],
        ]

        # Call the collate_fn method
        result = self.dataset.collate_fn_acoustic(data)

        # Check the output
        self.assertEqual(len(result), 12)

        # Check that all the batches are the same size
        for batch in result:
            self.assertEqual(len(batch), 2)

    def test_normalize_pitch(self):
        pitches = [
            torch.tensor([100.0, 200.0, 300.0]),
            torch.tensor([150.0, 250.0, 350.0]),
        ]

        result = self.dataset.normalize_pitch(pitches)

        expected_output = (100.0, 350.0, 225.0, 93.54143524169922)

        self.assertEqual(result, expected_output)

    def test_dataloader(self):
        # Create a DataLoader from the dataset
        dataloader = DataLoader(
            self.dataset,
            batch_size=self.batch_size,
            shuffle=False,
            collate_fn=self.dataset.collate_fn_acoustic,
        )

        iter_dataloader = iter(dataloader)

        # Iterate over the DataLoader and check the output
        for _, items in enumerate([next(iter_dataloader), next(iter_dataloader)]):
            # items = batch[0]

            # Check the batch size
            self.assertEqual(len(items), 12)

            for it in items:
                self.assertEqual(len(it), self.batch_size)


if __name__ == "__main__":
    unittest.main()

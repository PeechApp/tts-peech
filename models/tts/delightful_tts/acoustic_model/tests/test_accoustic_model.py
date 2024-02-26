import unittest

import torch
from torch.utils.data import DataLoader
import torchaudio

from models.config import AcousticENModelConfig, PreprocessingConfig

# TODO: profile deeply the memory usage
# from torch.profiler import profile, record_function, ProfilerActivity
from models.helpers import tools
from models.helpers.initializer import (
    get_test_configs,
    init_acoustic_model,
    init_forward_trains_params,
)
from models.tts.delightful_tts.acoustic_model.acoustic_model import AcousticModel
from training.datasets.libritts_dataset_acoustic import LibriTTSDatasetAcoustic


# AcousticModel test
# Integration test
class TestAcousticModel(unittest.TestCase):
    def setUp(self):
        # TODO: optimize the model, so that it can be tested with srink_factor=1
        # Get config with srink_factor=4
        # Memory error with srink_factor =< 2
        # Probably because of the size of the model, probably memory leak
        # Tried to profile the memory usage, but it didn't help
        (
            self.preprocess_config,
            self.model_config,
            self.acoustic_pretraining_config,
        ) = get_test_configs(srink_factor=4)

        # Based on speaker.json mock
        n_speakers = 10

        # Add AcousticModel instance
        self.acoustic_model, _ = init_acoustic_model(
            self.preprocess_config, self.model_config, n_speakers,
        )

        # Generate mock data for the forward pass
        self.forward_train_params = init_forward_trains_params(
            self.model_config,
            self.acoustic_pretraining_config,
            self.preprocess_config,
            n_speakers,
        )

    def test_freeze_unfreese_params_except_diffusion(self):
        acoustic_model = AcousticModel(
            self.preprocess_config,
            self.model_config,
            n_speakers=10,
        )
        # Freeze all parameters except diffusion
        acoustic_model.freeze_params_except_diffusion()

        for name, param in acoustic_model.named_parameters():
            if "diffusion" in name or "to_cond" in name:
                self.assertTrue(param.requires_grad)
            else:
                self.assertFalse(param.requires_grad)

        # Unfreeze all parameters
        acoustic_model.unfreeze_params(False, False)

        for param in acoustic_model.parameters():
            self.assertTrue(param.requires_grad)


    def test_get_embeddings(self):
        # Generate masks for padding positions in the source sequences and mel sequences
        # src_mask: Tensor containing the masks for padding positions in the source sequences. Shape: [1, batch_size]
        src_mask = tools.get_mask_from_lengths(self.forward_train_params.src_lens)

        # token_embeddings: Tensor containing the input sequences. Shape: [speaker_embed_dim, batch_size, speaker_embed_dim]
        # embeddings: Tensor containing the embeddings. Shape: [speaker_embed_dim, batch_size, speaker_embed_dim + lang_embed_dim]
        token_embeddings, embeddings = self.acoustic_model.get_embeddings(
            token_idx=self.forward_train_params.x,
            speaker_idx=self.forward_train_params.speakers,
            src_mask=src_mask,
            lang_idx=self.forward_train_params.langs,
        )

        self.assertEqual(
            token_embeddings.shape,
            torch.Size(
                [
                    self.model_config.speaker_embed_dim,
                    self.acoustic_pretraining_config.batch_size,
                    self.model_config.speaker_embed_dim,
                ],
            ),
        )
        self.assertEqual(
            embeddings.shape,
            torch.Size(
                [
                    self.model_config.speaker_embed_dim,
                    self.acoustic_pretraining_config.batch_size,
                    self.model_config.speaker_embed_dim
                    + self.model_config.lang_embed_dim,
                ],
            ),
        )

    def test_forward_train(self):
        self.preprocess_config = PreprocessingConfig("english_only")
        self.model_config = AcousticENModelConfig()

        acoustic_model = AcousticModel(
            self.preprocess_config,
            self.model_config,
            n_speakers=5392,
        )

        dataset = LibriTTSDatasetAcoustic(
            root="datasets_cache/LIBRITTS",
            lang="en",
            cache=False,
            cache_dir="datasets_cache",
            mem_cache=False,
            url="train-clean-100",
        )

        train_loader = DataLoader(
            dataset,
            batch_size=1,
            num_workers=2,
            persistent_workers=True,
            pin_memory=True,
            shuffle=False,
            collate_fn=dataset.collate_fn,
        )
        for batch in train_loader:
            (
                _,
                _,
                speakers,
                texts,
                src_lens,
                mels,
                pitches,
                pitches_stat,
                mel_lens,
                langs,
                attn_priors,
                _,
                energies,
            ) = batch
            result = acoustic_model.forward_train(
                x=texts,
                speakers=speakers,
                src_lens=src_lens,
                mels=mels,
                mel_lens=mel_lens,
                pitches=pitches,
                pitches_range=pitches_stat,
                langs=langs,
                attn_priors=attn_priors,
                energies=energies,
            )
            break

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 14)

    def test_average_utterance_prosody(self):
        u_prosody_pred = torch.randn(2, 5, self.model_config.encoder.n_hidden)
        src_mask = torch.tensor(
            [[False, True, True, True, True], [False, False, True, True, True]],
        )

        averaged_prosody_pred = self.acoustic_model.average_utterance_prosody(
            u_prosody_pred=u_prosody_pred, src_mask=src_mask,
        )

        self.assertEqual(
            averaged_prosody_pred.shape,
            torch.Size([2, 1, self.model_config.encoder.n_hidden]),
        )

    def test_forward(self):
        x = self.acoustic_model.forward(
            x=self.forward_train_params.x,
            pitches_range=self.forward_train_params.pitches_range,
            speakers=self.forward_train_params.speakers,
            langs=self.forward_train_params.langs,
            p_control=0.5,
            d_control=0.5,
        )

        # The last dim is not stable!
        self.assertEqual(x.shape[0], self.model_config.speaker_embed_dim)
        self.assertEqual(x.shape[1], self.preprocess_config.stft.n_mel_channels)

if __name__ == "__main__":
    unittest.main()

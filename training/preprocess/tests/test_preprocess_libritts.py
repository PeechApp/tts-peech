import unittest

import torch

from training.preprocess import PreprocessLibriTTS
from training.preprocess.preprocess_libritts import PreprocessAudioResult


class TestPreprocessLibriTTS(unittest.TestCase):
    def setUp(self):
        torch.random.manual_seed(42)
        self.preprocess_libritts = PreprocessLibriTTS()

    def test_call(self):
        # Set the sampling rate and duration of the audio signal
        sr_actual = 44100
        duration = 1.0

        # Set the frequency of the pitch (in Hz)
        pitch_freq = 440.0

        # Generate a time vector for the audio signal
        t = torch.linspace(0, duration, int(sr_actual * duration))

        # Generate a sinusoidal waveform with the specified pitch frequency
        audio = torch.sin(2 * torch.pi * pitch_freq * t)

        audio = audio.unsqueeze(0)

        raw_text = "Hello, world!"

        output = self.preprocess_libritts((audio, sr_actual, raw_text, raw_text, 0, 0, "0"))

        self.assertIsNotNone(output)

        if output is not None:
            self.assertIsInstance(output, PreprocessAudioResult)

            self.assertIsInstance(output.wav, torch.Tensor)
            self.assertIsInstance(output.mel, torch.Tensor)
            self.assertIsInstance(output.pitch, torch.Tensor)
            self.assertIsInstance(output.phones, torch.Tensor)
            self.assertIsInstance(output.raw_text, str)
            self.assertIsInstance(output.pitch_is_normalized, bool)

            self.assertEqual(output.wav.shape, torch.Size([22050]))
            self.assertEqual(output.mel.shape, torch.Size([100, 86]))
            self.assertEqual(output.pitch.shape, torch.Size([86]))

            torch.testing.assert_close(
                output.phones,
                torch.tensor([ 2., 10., 37., 14., 17., 45., 24., 39., 50., 14.,  6.,  3.]),
            )

            self.assertEqual(output.raw_text, "Hello, world!")
            self.assertFalse(output.pitch_is_normalized)

    def test_call_with_short_audio(self):
        audio = torch.randn(1, 22050)
        sr_actual = 22050
        raw_text = "Hello, world!"
        output = self.preprocess_libritts((audio, sr_actual, raw_text, raw_text, 0, 0, "0"))

        self.assertIsNone(output)

    def test_call_with_complicated_text(self):
        # Set the sampling rate and duration of the audio signal
        sr_actual = 44100
        duration = 10.0

        # Set the frequency of the pitch (in Hz)
        pitch_freq = 440.0

        # Generate a time vector for the audio signal
        t = torch.linspace(0, duration, int(sr_actual * duration))

        # Generate a sinusoidal waveform with the specified pitch frequency
        audio = torch.sin(2 * torch.pi * pitch_freq * t).unsqueeze(0)

        raw_text = r"""
        Hello, world! Wow!!!!! This is amazing?????
        It’s a beautiful day… 
        Mr. Smith paid $111 in U.S.A. on Dec. 17th. We paid $123 for this desk.
        """

        output = self.preprocess_libritts((audio, sr_actual, raw_text, raw_text, 0, 0, "0"))

        self.assertIsNotNone(output)

        if output is not None:
            self.assertEqual(output.attn_prior.shape, torch.Size([88, 861]))
            self.assertEqual(output.mel.shape, torch.Size([100, 861]))

            self.assertEqual(output.normalized_text, "Hello, world! Wow! This is amazing?It's a beautiful day. mister Smith paid one hundred and eleven dollars in USA on december seventeenth. We paid one hundred and twenty three dollars for this desk.")

            self.assertEqual(output.phones.shape, torch.Size([88]))
            self.assertEqual(len(output.phones_ipa), 160)

            self.assertEqual(output.wav.shape, torch.Size([220500]))

    def test_forward_with_long_audio(self):
        audio = torch.randn(1, 88200)
        sr_actual = 44100
        raw_text = "Hello, world!"
        output = self.preprocess_libritts((audio, sr_actual, raw_text, raw_text, 0, 0, "0"))

        self.assertIsNone(output)
    
    def test_beta_binomial_prior_distribution(self):
        phoneme_count = 10
        mel_count = 20
        prior_dist = self.preprocess_libritts.beta_binomial_prior_distribution(
            phoneme_count, mel_count
        )
        self.assertIsInstance(prior_dist, torch.Tensor)
        self.assertEqual(prior_dist.shape, (mel_count, phoneme_count))

if __name__ == "__main__":
    unittest.main()
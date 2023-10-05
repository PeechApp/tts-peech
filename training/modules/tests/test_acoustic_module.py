import unittest

import torch

from training.modules.acoustic_module import AcousticModule


class TestTrainAcousticModule(unittest.TestCase):
    def setUp(self):
        self.model = AcousticModule()
        pass

    def test_forward(self):
        x = torch.randn(1, 28 * 28)
        y = self.model(x)
        self.assertEqual(y.size(), torch.Size([1, 10]))

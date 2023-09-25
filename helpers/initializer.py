import torch

from typing import Tuple
from dataclasses import dataclass

from config import (
    AcousticModelConfigType,
    PreprocessingConfig,
    AcousticENModelConfig,
    AcousticPretrainingConfig,
    SUPPORTED_LANGUAGES,
)

from model.acoustic_model import AcousticModel

from model.attention.conformer import Conformer


@dataclass
class ConformerConfig:
    dim: int
    n_layers: int
    n_heads: int
    embedding_dim: int
    p_dropout: float
    kernel_size_conv_mod: int
    with_ff: bool


# Function to initialize a Conformer with a given AcousticModelConfigType configuration
def init_conformer(
    model_config: AcousticModelConfigType,
) -> Tuple[Conformer, ConformerConfig]:
    r"""
    Function to initialize a `Conformer` with a given `AcousticModelConfigType` configuration.

    Args:
        model_config (AcousticModelConfigType): The object that holds the configuration details.

    Returns:
        Conformer: Initialized Conformer object.

    The function sets the details of the `Conformer` object based on the `model_config` parameter.
    The `Conformer` configuration is set as follows:
    - dim: The number of hidden units, taken from the encoder part of the `model_config.encoder.n_hidden`.
    - n_layers: The number of layers, taken from the encoder part of the `model_config.encoder.n_layers`.
    - n_heads: The number of attention heads, taken from the encoder part of the `model_config.encoder.n_heads`.
    - embedding_dim: The sum of dimensions of speaker embeddings and language embeddings.
      The speaker_embed_dim and lang_embed_dim are a part of the `model_config.speaker_embed_dim`.
    - p_dropout: Dropout rate taken from the encoder part of the `model_config.encoder.p_dropout`.
      It adds a regularization parameter to prevent overfitting.
    - kernel_size_conv_mod: The kernel size for the convolution module taken from the encoder part of the `model_config.encoder.kernel_size_conv_mod`.
    - with_ff: A Boolean value denoting if feedforward operation is involved, taken from the encoder part of the `model_config.encoder.with_ff`.

    """
    conformer_config = ConformerConfig(
        dim=model_config.encoder.n_hidden,
        n_layers=model_config.encoder.n_layers,
        n_heads=model_config.encoder.n_heads,
        embedding_dim=model_config.speaker_embed_dim
        + model_config.lang_embed_dim,  # speaker_embed_dim + lang_embed_dim = 385
        p_dropout=model_config.encoder.p_dropout,
        kernel_size_conv_mod=model_config.encoder.kernel_size_conv_mod,
        with_ff=model_config.encoder.with_ff,
    )

    return Conformer(**vars(conformer_config)), conformer_config


@dataclass
class AcousticModelConfig:
    data_path: str
    preprocess_config: PreprocessingConfig
    model_config: AcousticENModelConfig
    fine_tuning: bool
    n_speakers: int


def init_acoustic_model(
    preprocess_config: PreprocessingConfig,
    model_config: AcousticENModelConfig,
    n_speakers: int = 10,
    data_path: str = "./model/acoustic_model/tests/mocks",
) -> Tuple[AcousticModel, AcousticModelConfig]:
    r"""
    Function to initialize an `AcousticModel` with given preprocessing and model configurations.

    Args:
        preprocess_config (PreprocessingConfig): Configuration object for pre-processing.
        model_config (AcousticENModelConfig): Configuration object for English Acoustic model.
        n_speakers (int, optional): Number of speakers. Defaults to 10.
        data_path (str, optional): Path to the data for the model. Defaults to "./model/acoustic_model/tests/mocks".

    Returns:
        AcousticModel: Initialized Acoustic Model.

    The function creates an `AcousticModelConfig` instance which is then used to initialize the `AcousticModel`.
    The `AcousticModelConfig` is configured as follows:
    - data_path: Path to the data for the model.
    - preprocess_config: Pre-processing configuration.
    - model_config: English Acoustic model configuration.
    - fine_tuning: Boolean flag set to True indicating the model is for fine-tuning.
    - n_speakers: Number of speakers.

    """
    # Create an AcousticModelConfig instance
    acoustic_model_config = AcousticModelConfig(
        data_path=data_path,
        preprocess_config=preprocess_config,
        model_config=model_config,
        fine_tuning=True,
        n_speakers=n_speakers,
    )

    return AcousticModel(**vars(acoustic_model_config)), acoustic_model_config


@dataclass
class ForwardTrainParams:
    x: torch.Tensor
    speakers: torch.Tensor
    src_lens: torch.Tensor
    mels: torch.Tensor
    mel_lens: torch.Tensor
    enc_len: torch.Tensor
    pitches: torch.Tensor
    langs: torch.Tensor
    attn_priors: torch.Tensor
    use_ground_truth: bool = True


def init_forward_trains_params(
    model_config: AcousticENModelConfig,
    acoustic_pretraining_config: AcousticPretrainingConfig,
    preprocess_config: PreprocessingConfig,
    n_speakers: int = 10,
) -> ForwardTrainParams:
    r"""
    Function to initialize the parameters for forward propagation during training.

    Args:
        model_config (AcousticENModelConfig): Configuration object for English Acoustic model.
        acoustic_pretraining_config (AcousticPretrainingConfig): Configuration object for acoustic pretraining.
        n_speakers (int, optional): Number of speakers. Defaults to 10.

    Returns:
        ForwardTrainParams: Initialized parameters for forward propagation during training.

    The function initializes the ForwardTrainParams object with the following parameters:
    - x: Tensor containing the input sequences. Shape: [speaker_embed_dim, batch_size]
    - speakers: Tensor containing the speaker indices. Shape: [speaker_embed_dim, batch_size]
    - src_lens: Tensor containing the lengths of source sequences. Shape: [batch_size]
    - mels: Tensor containing the mel spectrogram. Shape: [batch_size, speaker_embed_dim, encoder.n_hidden]
    - mel_lens: Tensor containing the lengths of mel sequences. Shape: [batch_size]
    - pitches: Tensor containing the pitch values. Shape: [batch_size, speaker_embed_dim, encoder.n_hidden]
    - langs: Tensor containing the language indices. Shape: [speaker_embed_dim, batch_size]
    - attn_priors: Tensor containing the attention priors. Shape: [batch_size, speaker_embed_dim, speaker_embed_dim]
    - use_ground_truth: Boolean flag indicating if ground truth values should be used or not.

    All the Tensors are initialized with random values.
    """
    return ForwardTrainParams(
        # x: Tensor containing the input sequences. Shape: [speaker_embed_dim, batch_size]
        x=torch.randint(
            1,
            255,
            (
                model_config.speaker_embed_dim,
                acoustic_pretraining_config.batch_size,
            ),
        ),
        # speakers: Tensor containing the speaker indices. Shape: [speaker_embed_dim, batch_size]
        speakers=torch.randint(
            1,
            n_speakers - 1,
            (
                model_config.speaker_embed_dim,
                acoustic_pretraining_config.batch_size,
            ),
        ),
        # src_lens: Tensor containing the lengths of source sequences. Shape: [batch_size]
        src_lens=torch.tensor([acoustic_pretraining_config.batch_size]),
        # mels: Tensor containing the mel spectrogram. Shape: [batch_size, stft.n_mel_channels, encoder.n_hidden]
        mels=torch.randn(
            model_config.speaker_embed_dim,
            preprocess_config.stft.n_mel_channels,
            model_config.encoder.n_hidden,
        ),
        # enc_len: Tensor containing the lengths of mel sequences. Shape: [speaker_embed_dim]
        enc_len=torch.cat(
            [
                torch.randint(
                    1,
                    model_config.speaker_embed_dim,
                    (model_config.speaker_embed_dim - 1,),
                ),
                torch.tensor([model_config.speaker_embed_dim]),
            ],
            dim=0,
        ),
        # mel_lens: Tensor containing the lengths of mel sequences. Shape: [batch_size]
        mel_lens=torch.cat(
            [
                torch.randint(
                    1,
                    model_config.speaker_embed_dim,
                    (model_config.speaker_embed_dim - 1,),
                ),
                torch.tensor([model_config.speaker_embed_dim]),
            ],
            dim=0,
        ),
        # pitches: Tensor containing the pitch values. Shape: [batch_size, speaker_embed_dim, encoder.n_hidden]
        pitches=torch.randn(
            acoustic_pretraining_config.batch_size,
            model_config.speaker_embed_dim,
            model_config.encoder.n_hidden,
        ),
        # langs: Tensor containing the language indices. Shape: [speaker_embed_dim, batch_size]
        langs=torch.randint(
            1,
            len(SUPPORTED_LANGUAGES) - 1,
            (
                model_config.speaker_embed_dim,
                acoustic_pretraining_config.batch_size,
            ),
        ),
        # attn_priors: Tensor containing the attention priors. Shape: [batch_size, speaker_embed_dim, speaker_embed_dim]
        attn_priors=torch.randn(
            acoustic_pretraining_config.batch_size,
            model_config.speaker_embed_dim,
            model_config.speaker_embed_dim,
        ),
        use_ground_truth=True,
    )

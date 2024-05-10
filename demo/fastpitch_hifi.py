from gradio import Dropdown, Interface, Textbox
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder
import torch

# Download and load the pretrained tacotron2 model
spec_generator = SpectrogramGenerator.from_pretrained("tts_en_fastpitch_multispeaker")

# Download and load the pretrained hifi-gan model
vocoder = Vocoder.from_pretrained("tts_en_hifitts_hifigan_ft_fastpitch")

speakers = {
    "Cori Samuel": 92,
    "Phil Benson": 6097,
    "John Van Stan": 9017,
    "Mike Pelton": 6670,
    "Tony Oliva": 6671,
    "Maria Kasper": 8051,
    "Helen Taylor": 9136,
    "Sylviamb": 11614,
    "Celine Major": 11697,
    "LikeManyWaters": 12787,
}

speakers_names = list(speakers.keys())
speakers_ids = list(speakers.values())


def generate_audio(text: str, speaker: str):
    with torch.no_grad():
        # All spectrogram generators start by parsing raw strings to a tokenized version of the string
        parsed = spec_generator.parse(text)
        # Then take the tokenized string and produce a spectrogram
        spectrogram = spec_generator.generate_spectrogram(
            tokens=parsed,
            speaker=speakers[speaker],
        )
        # Finally, a vocoder converts the spectrogram to audio
        audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)

    audio = audio.squeeze().detach().cpu().numpy()

    return 44100, audio


interfaceFastpichHifi = Interface(
    generate_audio,
    [
        Textbox(
            label="Text",
            value="As the snake shook its head, a deafening shout behind Harry made both of them jump.",
        ),
        Dropdown(
            label="Speaker",
            choices=list(speakers_names),
            value=speakers_names[0],
        ),
    ],
    outputs="audio",
)

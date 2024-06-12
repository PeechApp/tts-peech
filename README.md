# TTS-Framework

[DelightfulTTS: The Microsoft Speech Synthesis System for Blizzard Challenge 2021](https://arxiv.org/abs/2110.12612)

<p align="center">
  <a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>
  <a href="https://lightning.ai/"><img alt="Lightning" src="https://img.shields.io/badge/-Lightning-792ee5?logo=pytorchlightning&logoColor=white"></a>
  <a href="https://huggingface.co/spaces/peechapp/PeechTTSv22050"  style='padding-left: 0.5rem;'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-orange'></a>
</p>

## [A comprehensive review of opensource Text-to-Speech (TTS) Models](https://nickovchinnikov.github.io/tts-framework/review/)

Medium series (with memes): [Machine Learning Text-To-Speech: Intro, Little Theory and Math](https://medium.com/@peechapp/text-to-speech-models-part-1-intro-little-theory-and-math-0ffa5d3e0e3f)

## Demo and weights

**Weights can be found inside the hf space.**
![Demo](docs-md/assets/demo_space.png)

### DelightfulTTS + UnivNet, 22.05 khz, [check hf space demo PeechTTSv22050](https://huggingface.co/spaces/peechapp/PeechTTSv22050)

DelightfulTTS Weights: [epoch=5816-step=390418.ckpt](https://huggingface.co/spaces/peechapp/PeechTTSv22050/blob/main/epoch%3D5816-step%3D390418.ckpt)

Univnet Weights: [vocoder_pretrained.pt](https://huggingface.co/spaces/peechapp/PeechTTSv22050/blob/main/vocoder_pretrained.pt)

### DelightfulTTS + HifiGAN, 44.1 khz, [check hf space demo PeechTTSv44100](https://huggingface.co/spaces/peechapp/PeechTTSv44100)

DelightfulTTS Weights: [epoch=2450-step=183470.ckpt](https://huggingface.co/spaces/peechapp/PeechTTSv44100/blob/main/epoch%3D2450-step%3D183470.ckpt)

HifiGAN Weights: [epoch=19-step=44480.ckpt](https://huggingface.co/spaces/peechapp/PeechTTSv44100/blob/main/epoch%3D19-step%3D44480.ckpt)

## Run locally

### Install deps

```bash
sudo apt install ffmpeg libasound2-dev build-essential espeak-ng -y
```

Create env from the `environment.yml` file:

```bash
conda env create -f environment.yml

# After the setup
conda activate tts_framework

# Install torch
pip install --upgrade --force-reinstall --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

# Install nemo
pip install nemo_toolkit['all']

# Run demo
python app.py
```

## Generate docs:

```
# live preview server
mkdocs serve

# build a static site from your Markdown files
mkdocs build
```

## Test cases:

```
python -m unittest discover -v
```

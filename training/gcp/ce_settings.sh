# Update the system
sudo apt update -y && sudo apt upgrade -y

# Install deps
sudo apt install ffmpeg libasound2-dev -y

sudo apt install build-essential -y

# espeak-ng
sudo apt-get install espeak-ng -y

# Copy the datasets_cache folder metadata
mkdir -p ./tts-framework/datasets_cache/LIBRITTS/LibriTTS/

gsutil cp -r gs://tts-training-bucket/datasets_cache/** ./tts-framework/datasets_cache/LIBRITTS/LibriTTS/

gsutil cp gs://tts-training-bucket/vocoder_pretrained.pt ./tts-framework/checkpoints/
gsutil cp gs://tts-training-bucket/en_us_cmudict_ipa_forward.pt ./tts-framework/checkpoints/


# Download the dataset train-other-500
curl -O https://us.openslr.org/resources/141/train_other_500.tar.gz
mv train_other_500.tar.gz ./tts-framework/datasets_cache/LIBRITTS/

tar -xzvf ./tts-framework/datasets_cache/LIBRITTS/train_other_500.tar.gz -C ./tts-framework/datasets_cache/LIBRITTS/
mv ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R/train-other-500 ./tts-framework/datasets_cache/LIBRITTS/LibriTTS
rm -r ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R


# Download the dataset train_clean_360
curl -O http://us.openslr.org/resources/141/train_clean_360.tar.gz
mv train_clean_360.tar.gz ./tts-framework/datasets_cache/LIBRITTS/

tar -xzvf ./tts-framework/datasets_cache/LIBRITTS/train_clean_360.tar.gz -C ./tts-framework/datasets_cache/LIBRITTS/
mv ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R/train-clean-360 ./tts-framework/datasets_cache/LIBRITTS/LibriTTS
rm -r ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R

# Download the dataset train_clean_100
curl -O https://us.openslr.org/resources/141/train_clean_100.tar.gz
mv train_clean_100.tar.gz ./tts-framework/datasets_cache/LIBRITTS/

tar -xzvf ./tts-framework/datasets_cache/LIBRITTS/train_clean_100.tar.gz -C ./tts-framework/datasets_cache/LIBRITTS/
mv ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R/train-clean-100 ./tts-framework/datasets_cache/LIBRITTS/LibriTTS
rm -r ./tts-framework/datasets_cache/LIBRITTS/LibriTTS_R

# Add envs dir for conda envs
# conda config --add envs_dirs /home/jupyter/envs

conda env create -f ./tts-framework/environment.yml
# conda config --show-sources
conda activate tts_framework

cp ./tts-framework/models/tts/delightful_tts/train/train.py ./tts-framework

# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/conda/lib

# And then check the torch version and cuda version
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.backends.cudnn.version())"

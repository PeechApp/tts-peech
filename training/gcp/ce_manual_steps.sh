# Do ce_manual_steps.sh first, then run this script
# Install Cloud Storage FUSE
# export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`

# echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list

# curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# sudo apt-get install fuse gcsfuse -y

# # Check the gcsfuse version
# gcsfuse -v

##########################################

# Update the system
# sudo apt update && sudo apt upgrade -y

# Install CUDA drivers
# sudo apt -y install cuda-drivers
# sudo apt -y install nvidia-cuda-toolkit


# Install git
# sudo apt install git -y

# # Clone the repo
# git clone git@github.com:nickovchinnikov/tts-framework.git

# Do this before running the script ce_settings.sh
# Install miniconda
# curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

curl -O https://repo.anaconda.com/archive/Anaconda3-2024.02-1-Linux-x86_64.sh

# bash Miniconda3-latest-Linux-x86_64.sh

# # bash Miniconda3-latest-Linux-x86_64.sh
# source ~/.bashrc

# # Do the gcould init (auth)
# gcloud init

# Create a ssh key and add it to the github
ssh-keygen -t rsa -f ~/.ssh/id_rsa -q -N ""

# Add the key to the github and add the github to the known hosts
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

###############################################
# Mount the disc
###############################################

# List the disks
# lsblk -o NAME,HCTL,SIZE,MOUNTPOINT | grep nvme

# Check the devices
ls -l /dev/disk/by-id/google-*

# Choose and format the disk
sudo mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/disk/by-id/google-local-nvme-ssd-0

# Mount the disk
# mount point
sudo mkdir -p /mnt/disks/training-disk
# mount the disk
sudo mount -o discard,defaults /dev/disk/by-id/google-local-nvme-ssd-0 /mnt/disks/training-disk
# Change the owner
sudo chmod a+w /mnt/disks/training-disk


# Configure automatic mounting on VM restart
sudo cp /etc/fstab /etc/fstab.backup
# Use the blkid command to list the UUID for the disk.
sudo blkid /dev/disk/by-id/google-local-nvme-ssd-0


# Example:
# /dev/disk/by-id/google-local-nvme-ssd-0: UUID="35c0d7f9-bf93-4dce-8dd9-fe2b5ba8e867" BLOCK_SIZE="4096" TYPE="ext4"
# Change the /etc/fstab file to mount the disk automatically after a VM restart.
###############################################
# cat /etc/fstab:
# UUID=35c0d7f9-bf93-4dce-8dd9-fe2b5ba8e867 /mnt/disks/training-disk ext4 discard,defaults 0 2

# Choose the mounted disk
# Change the directory to the mounted disk
cd /mnt/disks/training-disk

# Clone the repo
git clone git@github.com:nickovchinnikov/tts-framework.git

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/conda/lib
# Permanently add the path to the LD_LIBRARY_PATH
# echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/conda/lib' >> ~/.profile

# After the setup
conda activate tts_framework

# First reinstall the lightning
pip install --upgrade --force-reinstall lightning

# Version 11.8
pip install --upgrade --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Version 12.1 nightly (the fastest one)
pip install --upgrade --force-reinstall --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

# Version 12.1
pip install --upgrade --force-reinstall torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.backends.cudnn.version())"

python -c "import torchaudio; print(torchaudio.__version__);"
python -c "import torchvision; print(torchvision.__version__);"
python -c "import lightning; print(lightning.__version__);"

# Add conda env to jupyter notebook kernel
python -m ipykernel install --user --name tts_framework --display-name "TTS-Framework"

python -m ipykernel install --user --name coqui-ai --display-name "Coqui.ai"

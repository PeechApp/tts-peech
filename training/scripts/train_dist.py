import torch

from lightning.pytorch import Trainer
from lightning.pytorch.accelerators import find_usable_cuda_devices # type: ignore
from lightning.pytorch.loggers import TensorBoardLogger

from training.modules import AcousticModule

print("usable_cuda_devices: ", find_usable_cuda_devices())

# Set the precision of the matrix multiplication to float32 to improve the performance of the training
torch.set_float32_matmul_precision("high")

default_root_dir="logs"

ckpt_acoustic="./checkpoints/epoch=189-step=92340.ckpt"

ckpt_vocoder="./checkpoints/vocoder.ckpt"

tensorboard = TensorBoardLogger(
    save_dir=default_root_dir,
)

trainer = Trainer(
    accelerator="cuda",
    devices=-1,
    strategy="ddp",
    logger=tensorboard,
    # Save checkpoints to the `default_root_dir` directory
    default_root_dir=default_root_dir,
    accumulate_grad_batches=10,
    max_epochs=-1,
    enable_model_summary=False,
)

module = AcousticModule()

train_dataloader = module.train_dataloader()

trainer.fit(
    model=module,
    train_dataloaders=train_dataloader,
    # Resume training states from the checkpoint file
    ckpt_path=ckpt_acoustic,
)

import torch

CONTEXT_LENGTH = 1024
MODEL_NAME = "gpt2"
SEED = 69420
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

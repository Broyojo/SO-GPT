import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from config import CONTEXT_LENGTH, DEVICE, MODEL_NAME, SEED

model = AutoModelForCausalLM.from_pretrained("models/gpt2-python/checkpoint-5000").to(
    DEVICE
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, padding_side="left")

with torch.no_grad():
    encoded = tokenizer(
        "Title:How do I train MNIST with Keras?\nBody:<p>How do I do this?</p>\nAnswer:",
        return_tensors="pt",
    ).to(DEVICE)
    outputs = model.generate(
        **encoded,
        max_length=CONTEXT_LENGTH,
        top_k=50,
        do_sample=True,
        temperature=0.7,
        top_p=1.0,
        num_return_sequences=1,
        early_stopping=True,
    )[0]
    decoded = tokenizer.decode(outputs, skip_special_tokens=True)
    print(decoded)

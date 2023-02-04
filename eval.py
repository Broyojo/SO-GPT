import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = GPT2TokenizerFast.from_pretrained(
        "gpt2",
        pad_token="<|endoftext|>",
        padding_side="left",
    )
    model = GPT2LMHeadModel.from_pretrained("models/cooking").to(device)

    with torch.no_grad():
        prompt = "<p>How do you make scrambled eggs?</p><endoftext>"
        encoding = tokenizer(
            prompt,
            padding=True,
            return_tensors="pt",
        ).to(device)

        output = model.generate(
            **encoding,
            max_length=1024,
            num_return_sequences=1,
            top_k=50,
            top_p=1,
            do_sample=True,
            bos_token_id=tokenizer.bos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )[0]

        output = tokenizer.decode(output, skip_special_tokens=True)

    with open("viewer.html", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()

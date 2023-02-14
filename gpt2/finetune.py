import os

import torch
from datasets import load_dataset
from transformers import (
    DataCollatorForLanguageModeling,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
    Trainer,
    TrainingArguments,
)


def main():
    model_name = "gpt2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = GPT2TokenizerFast.from_pretrained(
        model_name,
        pad_token="<|endoftext|>",
        padding_side="left",
    )
    model = GPT2LMHeadModel.from_pretrained(model_name).to(device)
    model.resize_token_embeddings(len(tokenizer))

    def tokenize(example):
        encoded = tokenizer(
            example["text"],
            truncation=True,
            max_length=1024,
            return_overflowing_tokens=True,
            return_length=True,
        )
        return {"input_ids": encoded["input_ids"]}

    dataset = (
        load_dataset("json", data_files="dataset.json", split="train", field="data")
        .shuffle()
        .map(
            tokenize,
            batched=True,
            remove_columns=["text"],
            num_proc=os.cpu_count(),
        )
        .train_test_split(0.01)
    )

    print(dataset)

    output_dir = "models/stackoverflow-5mil"

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=1,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=8,
        save_total_limit=5,
        save_steps=5000,
        eval_steps=5000,
        logging_steps=50,
        logging_strategy="steps",
        evaluation_strategy="steps",
        prediction_loss_only=False,
        remove_unused_columns=False,
        load_best_model_at_end=True,
        fp16=True if device == "cuda" else False,
        overwrite_output_dir=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
    )

    trainer.train()
    trainer.save_model(output_dir)

    # print(tokenizer.decode(dataset["train"][0]["input_ids"]))


if __name__ == "__main__":
    main()

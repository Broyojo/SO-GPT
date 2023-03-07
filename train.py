import os

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

from config import CONTEXT_LENGTH, MODEL_NAME, SEED

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, pad_token_id=tokenizer.pad_token_id
)
data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
device = "cuda" if torch.cuda.is_available() else "cpu"


def process(example):
    title = example["title"]
    question_body = example["question_body"]
    answer_body = example["answer_body"]

    concatenated = (
        f"Title:{title}\nQuestion:{question_body}\nAnswer:{answer_body}<|endoftext|>"
    )

    return {"text": concatenated}


def encode(example):
    encoded = tokenizer(
        example["text"],
        truncation=True,
        max_length=CONTEXT_LENGTH,
        return_overflowing_tokens=True,
        return_length=True,
    )

    return {"input_ids": encoded["input_ids"]}


# keep all answers, even if they are duplicates for now
dataset = (
    load_dataset("koutch/stackoverflow_python", split="train")
    .shuffle(SEED)
    .map(
        process,
        num_proc=os.cpu_count(),
        remove_columns=[
            "title",
            "question_id",
            "question_body",
            "question_score",
            "question_date",
            "answer_id",
            "answer_body",
            "answer_score",
            "answer_date",
            "tags",
        ],
    )
    .map(
        encode,
        batched=True,
        remove_columns=["text"],
        num_proc=os.cpu_count(),
    )
    .train_test_split(0.001)
)

print(dataset)

# tokens = dataset["train"][8]["input_ids"]

# print(tokenizer.decode(tokens))
# print("len", len(tokens))

# quit()
training_args = TrainingArguments(
    output_dir="models/gpt2-python",
    half_precision_backend="auto",
    fp16=True,
    fp16_full_eval=True,
    auto_find_batch_size=True,  # on 2080ti: 2 train, 8 eval
    num_train_epochs=1.0,
    load_best_model_at_end=True,
    evaluation_strategy="steps",
    full_determinism=True,
    seed=SEED,
)

trainer = Trainer(
    model=model,
    tokenizer=tokenizer,
    data_collator=data_collator,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

trainer.train()
trainer.save_model()

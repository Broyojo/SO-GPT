import json


def main():
    with open("pairs.json", "r") as f:
        pairs = json.load(f)

    texts = []

    for pair in pairs:
        question = pair["question"]
        answer = pair["answer"]
        # maybe think of a better scheme for the dataset (maybe use Question: and Answer: labels instead of special tokens)
        texts.append({"text": f"Question:\n{question}\nAnswer:\n{answer}<|endoftext|>"})

    with open("dataset.json", "w") as f:
        json.dump({"data": texts}, f)


if __name__ == "__main__":
    main()

import json


def main():
    with open("pairs.json", "r") as f:
        pairs = json.load(f)

    texts = []

    for pair in pairs:
        question = pair["question"]
        answer = pair["answer"]
        texts.append({"text": f"{question}<|endoftext|>{answer}<|endoftext|>"})

    with open("dataset.json", "w") as f:
        json.dump({"data": texts}, f)


if __name__ == "__main__":
    main()

import json
import xml.etree.ElementTree as ET

from alive_progress import alive_it


def main():
    with open("../data/pairs.json", "r") as f:
        pairs = json.load(f)

    posts_path = "../data/cooking/Posts.xml"

    list_thing = []

    for pair in pairs.items():
        list_thing.append(pair)

    list_thing.sort(key=lambda t: t[1]["question_score"], reverse=True)

    # pick top 5000 questions
    pairs = dict(list_thing[:100])

    print(pairs)

    quit()

    for _, post in alive_it(
        ET.iterparse(posts_path), title=f"Reading posts from {posts_path}..."
    ):
        if post.tag != "row":
            continue

        post = dict(post.items())

        if post["Id"] in pairs:
            answer_id = pairs[post["Id"]]["answer_id"]
            answer_score = pairs[post["Id"]]["answer_score"]
            question_score = pairs[post["Id"]]["question_score"]

    # with open("gpt3-data.json", "a") as f:
    #     for pair in pairs:
    #         question = pair["question"]
    #         answer = pair["answer"]

    #         f.write(json.dumps({"prompt": question, "completion": answer}))


if __name__ == "__main__":
    main()

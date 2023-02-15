import json
import xml.etree.ElementTree as ET

from alive_progress import alive_it


def main():
    create_dataset("./data/stackoverflow/Posts.xml", max=1000) # 520,000 ~ 1% of all stack overflow questions and answers (not evenly distributed though)


def create_dataset(posts_path, max=1e9, every=10):
    questions = {}
    answers = {}
    pairs = []
    posts = 0
    
    for _, post in alive_it(
        ET.iterparse(posts_path), title=f"Reading posts from {posts_path}..."
    ):
        if post.tag != "row" or posts % every != 0:
            continue

        if posts >= max:
            break

        attribs = post.attrib
        id = attribs["Id"]
        body = attribs["Body"]
        score = int(attribs["Score"])

        match attribs["PostTypeId"]:
            case "1":
                questions[id] = {
                    "title": attribs["Title"],
                    "body": body,
                    "score": score,
                }
            case "2":
                answers[id] = {
                    "parent": attribs["ParentId"],
                    "body": body,
                    "score": score,
                }
        
        posts += 1

    pairs = {} # question_id -> { question, answer }

    for (id, answer) in alive_it(answers.items(), title=f"Creating question-answer pairs..."):
        if answer["parent"] in questions:
            if answer["parent"] not in pairs:
                pairs[answer["parent"]] = {
                    "question": questions[answer["parent"]],
                    "answer": answer,
                }
            else:
                if answer["score"] > pairs[answer["parent"]]["answer"]["score"]:
                    pairs[answer["parent"]]["answer"] = answer

    with open("data.json", "w") as f:
        json.dump(list(pairs.values()), f)

if __name__ == "__main__":
    main()
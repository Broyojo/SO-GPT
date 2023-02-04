import json
import random
import xml.etree.ElementTree as ET

from alive_progress import alive_it

# answer: select the top voted answer (putting trust in the community rather than the question-asker)

# question posts: PostTypeId = 1
# answer posts: PostTypeId = 2, ParentId = question id

# TODO: use https://github.com/StackExchange/Stacks-Editor as the text editor for the application. maybe have the same thing as the preview so they look like from Stack Overflow?


def main():
    # extract all posts from data dump
    posts_path = "data/cooking/Posts.xml"
    tree = ET.parse(posts_path)
    root = tree.getroot()
    posts = {}
    for post in alive_it(root, title=f"Reading posts from {posts_path}..."):
        items = dict(post.items())
        posts[items["Id"]] = items

    # get all (question, top answer) pairs
    question_answers = {}
    for answer in filter(lambda p: p["PostTypeId"] == "2", posts.values()):
        question_id = answer["ParentId"]
        if question_id not in question_answers:
            question_answers[question_id] = []
        question_answers[question_id].append(answer)

    question_answer_pairs = []
    for question_id, answers in question_answers.items():
        top_voted_answer = max(answers, key=lambda a: int(a["Score"]))
        question_answer_pairs.append((posts[question_id], top_voted_answer))

    print(
        f"Loaded {len(question_answer_pairs)} question-answer pairs ({len(question_answer_pairs)*2} posts) out of {len(posts)} total posts"
    )

    pair = random.choice(question_answer_pairs)

    question_body = pair[0]["Body"]

    answer_body = pair[1]["Body"]

    with open("viewer.html", "w") as f:
        f.write(question_body + "<hr>" + answer_body)

    print(f"Question ID: {pair[0]['Id']}")
    print(f"Answer ID: {pair[1]['Id']}")

    with open("pairs.json", "w") as f:
        pairs = [
            {"question": q["Body"], "answer": a["Body"]}
            for (q, a) in question_answer_pairs[:100]
        ]
        json.dump(pairs, f)


if __name__ == "__main__":
    main()

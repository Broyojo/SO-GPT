import random
import xml.etree.ElementTree as ET
from pathlib import Path
from pprint import pprint

from alive_progress import alive_it

# answer: select the top voted answer (putting trust in the community rather than the question-asker)

# question posts: PostTypeId = 1
# answer posts: PostTypeId = 2, ParentId = question id


def main():
    posts_path = "data/meta/Posts.xml"
    tree = ET.parse(posts_path)
    root = tree.getroot()
    posts = {}
    for post in alive_it(root, title=f"Reading posts from {posts_path}..."):
        items = dict(post.items())
        posts[items["Id"]] = items

    answered_ids = set()
    qa_pairs = []

    for answer in filter(lambda p: p["PostTypeId"] == "2", posts.values()):
        question_id = answer["ParentId"]
        if question_id in answered_ids:
            continue
        question = posts[question_id]
        answered_ids.add(question_id)
        qa_pairs.append((question, answer))

    print(
        f"Loaded {len(qa_pairs)} question-answer pairs ({len(qa_pairs)*2} posts) out of {len(posts)} total posts"
    )

    pair = random.choice(qa_pairs)

    question_body = pair[0]["Body"]

    answer_body = pair[1]["Body"]

    with open("index.html", "w") as f:
        f.write(question_body + "<hr>" + answer_body)


if __name__ == "__main__":
    main()

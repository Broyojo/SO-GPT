import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt

# import matplotlib.pyplot as plt
from alive_progress import alive_it

# max questions: https://stackexchange.com/sites?view=list#questions


@dataclass
class Question:
    id: str
    num_answers: int
    score: int


@dataclass
class Answer:
    id: str
    parent_id: str
    score: int


@dataclass
class Pair:
    question: Optional[Question]
    answer: Optional[Answer]
    num_answers_seen: int


def read_posts(posts_path: str, total: int):
    for _, post in alive_it(
        ET.iterparse(posts_path),
        title=f"Reading posts from {posts_path}...",
        total=total,
    ):
        if post.tag == "row":
            match post.attrib["PostTypeId"]:
                case "1":
                    num_answers = int(post.attrib["AnswerCount"])
                    if num_answers > 0:
                        yield Question(
                            id=post.attrib["Id"],
                            num_answers=num_answers,
                            score=int(post.attrib["Score"]),
                        )
                case "2":
                    yield Answer(
                        id=post.attrib["Id"],
                        parent_id=post.attrib["ParentId"],
                        score=int(post.attrib["Score"]),
                    )
        post.clear()  # very important, otherwise OOM error!!


def main():
    POSTS_PATH = "./data/cooking/Posts.xml"

    pairs: dict[str, Pair] = {}
    y = []

    with open("posts.txt", "a") as f:
        for post in read_posts(POSTS_PATH, total=58_000_000):
            y.append(len(pairs))
            match post:
                case Question(id, _, score):
                    if id not in pairs:
                        # pair does not exist
                        pairs[id] = Pair(
                            question=post,
                            answer=None,
                            num_answers_seen=0,
                        )
                    else:
                        # pair has an answer
                        pairs[id].question = post

                        if pairs[id].num_answers_seen >= pairs[id].question.num_answers:  # type: ignore
                            f.write(f"{id} {score} {pairs[id].answer.id}\n")  # type: ignore
                            del pairs[id]
                case Answer(id, parent_id, score):
                    if parent_id not in pairs:
                        # pair does not exist
                        pairs[parent_id] = Pair(
                            question=None,
                            answer=post,
                            num_answers_seen=1,
                        )
                    elif pairs[parent_id].question == None:
                        # pair has an answer but not a question
                        if score > pairs[parent_id].answer.score:  # type: ignore
                            pairs[parent_id].answer = post
                        pairs[parent_id].num_answers_seen += 1
                    else:
                        # pair has a question
                        if pairs[parent_id].answer == None:
                            # pair has no answer
                            pairs[parent_id].answer = post
                            pairs[parent_id].num_answers_seen = 1
                        elif score > pairs[parent_id].answer.score:  # type: ignore
                            # pair has both
                            pairs[parent_id].answer = post
                        if (
                            pairs[parent_id].num_answers_seen
                            >= pairs[parent_id].question.num_answers  # type: ignore
                        ):
                            f.write(f"{parent_id} {pairs[parent_id].question.score} {id}\n")  # type: ignore
                            del pairs[parent_id]
                            continue

                        pairs[parent_id].num_answers_seen += 1

        keys_to_remove = []

        # clean up the last posts
        for id, post in pairs.items():
            if post.num_answers_seen >= post.question.num_answers:  # type: ignore
                f.write(f"{id} {post.question.score} {post.answer.id}\n")  # type: ignore
                keys_to_remove.append(id)

        for key in keys_to_remove:
            del pairs[key]

    print(f"{len(pairs)} unmatched pairs")
    for pair in pairs.values():
        print(pair)

    plt.plot(y)
    print(f"max len: {max(y)}")
    print(f"total: {len(y)}")
    print(
        f"space reduction: {(len(y) - max(y)) / len(y) * 100:.{2}f}%",
    )
    plt.show()


if __name__ == "__main__":
    main()

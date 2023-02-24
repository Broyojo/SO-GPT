import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional

from alive_progress import alive_it


@dataclass
class Question:
    id: str
    num_answers: int
    score: int
    title: str
    body: str


@dataclass
class Answer:
    id: str
    parent_id: str
    score: int
    body: str


@dataclass
class Pair:
    question: Optional[Question]
    answer: Optional[Answer]


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
                            title=post.attrib["Title"],
                            body=post.attrib["Body"],
                        )
                case "2":
                    yield Answer(
                        id=post.attrib["Id"],
                        parent_id=post.attrib["ParentId"],
                        score=int(post.attrib["Score"]),
                        body=post.attrib["Body"],
                    )
        post.clear()  # very important, otherwise OOM error!!


def main():
    POSTS_PATH = "data/cooking/Posts.xml"

    # max questions: https://stackexchange.com/sites?view=list#questionss

    create_dataset(
        posts_path=POSTS_PATH, total=88706, top_num=30, dataset_path="dataset.json"
    )


def create_dataset(posts_path, total, top_num, dataset_path):
    top_pairs: list[Pair] = []

    # extract top questions first
    for post in read_posts(posts_path, total=total):
        match post:
            case Question(id, num_answers, score, title, body):
                if len(top_pairs) < top_num:
                    top_pairs.append(Pair(question=post, answer=None))
                elif score >= top_pairs[0].question.score:  # type: ignore
                    top_pairs.append(Pair(question=post, answer=None))
                    top_pairs.sort(key=lambda p: p.question.score)  # type: ignore

                    if len(top_pairs) > top_num:
                        top_pairs = top_pairs[len(top_pairs) - top_num :]

    pairs = {pair.question.id: pair for pair in top_pairs}  # type: ignore

    # find highest voted answer for top questions
    for post in read_posts(posts_path, total=total):
        match post:
            case Answer(id, parent_id, score, body):
                if parent_id in pairs:
                    if pairs[parent_id].answer == None:
                        pairs[parent_id].answer = post
                    elif score > pairs[parent_id].answer.score:
                        pairs[parent_id].answer = post

    # write question-answer pairs to dataset file
    with open(dataset_path, "a") as f:
        for pair in pairs.values():
            f.write(
                json.dumps(
                    {
                        "prompt": f"Title: {pair.question.title}\nBody:\n{pair.question.body}",
                        "completion": f"Answer:\n{pair.answer.body}",
                    }
                )
            )


if __name__ == "__main__":
    main()

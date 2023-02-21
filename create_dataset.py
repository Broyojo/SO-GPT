import json
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
from alive_progress import alive_it

# max questions: https://stackexchange.com/sites?view=list#questions


def main():
    POSTS_PATH = "./data/stackoverflow/Posts.xml"

    pairs = {}
    # lengths = []

    # use an iterator to clean things up here
    rows = filter(
        lambda r: r.tag == "row",
        map(
            lambda t: t[1],
            alive_it(
                ET.iterparse(POSTS_PATH),
                title=f"Reading posts from {POSTS_PATH}...",
            ),
        ),
    )

    with open("posts.txt", "a") as f:
        for row in rows:
            # lengths.append(len(pairs))
            post_attribs = row.attrib
            post_id = post_attribs["Id"]
            post_type = post_attribs["PostTypeId"]
            post_score = int(post_attribs["Score"])

            match post_type:
                case "1":
                    # post is a question

                    number_of_answers = int(post_attribs["AnswerCount"])

                    # if question has no answers, then it is useless and will be skipped
                    if number_of_answers == 0:
                        continue

                    if post_id not in pairs:
                        # answer does not exist
                        pairs[post_id] = {
                            "question score": post_score,
                            "number of answers": number_of_answers,
                        }
                    else:
                        # answer was found, but question not found
                        pairs[post_id]["question score"] = post_score
                        pairs[post_id]["number of answers"] = number_of_answers

                        # delete entry if all answers have been found
                        if (
                            pairs[post_id]["answers seen"]
                            >= pairs[post_id]["number of answers"]
                        ):
                            f.write(
                                f"{post_id} {post_score} {pairs[post_id]['answer id']}\n"
                            )
                            del pairs[post_id]
                case "2":
                    # post is an answer
                    parent_id = post_attribs["ParentId"]

                    if parent_id not in pairs:
                        # question does not exist
                        pairs[parent_id] = {
                            "answer id": post_id,
                            "answer score": post_score,
                            "answers seen": 1,
                        }
                    elif "question score" not in pairs[parent_id]:
                        # question has not been found yet, but there is at least one answer to it
                        continue
                    else:
                        # question exists
                        if "answer id" not in pairs[parent_id]:
                            # no answers have been found yet
                            pairs[parent_id]["answer id"] = post_id
                            pairs[parent_id]["answer score"] = post_score
                            pairs[parent_id]["answers seen"] = 1
                        elif post_score > pairs[parent_id]["answer score"]:
                            # at least one answer has been found and a comparison must be made
                            pairs[parent_id]["answer id"] = post_id
                            pairs[parent_id]["answer score"] = post_score

                        if (
                            pairs[parent_id]["answers seen"]
                            >= pairs[parent_id]["number of answers"]
                        ):
                            # delete entry if all answers have been found
                            f.write(
                                f"{parent_id} {pairs[parent_id]['question score']} {pairs[parent_id]['answer id']}\n"
                            )
                            del pairs[parent_id]
                            continue

                        # increment number of answers seen
                        pairs[parent_id]["answers seen"] += 1
    # plt.plot(lengths)
    # print(f"max len: {max(lengths)}")
    # print(f"total: {len(lengths)}")
    # print(
    #     f"space reduction: {(len(lengths) - max(lengths)) / len(lengths) * 100:.{2}f}%",
    # )
    # plt.show()


if __name__ == "__main__":
    main()

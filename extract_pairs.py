import json
import xml.etree.ElementTree as ET

from alive_progress import alive_it

# answer: select the top voted answer (putting trust in the community rather than the question-asker)

# question posts: PostTypeId = 1
# answer posts: PostTypeId = 2, ParentId = question id

# TODO: use https://github.com/StackExchange/Stacks-Editor as the text editor for the application. maybe have the same thing as the preview so they look like from Stack Overflow?


def main():
    posts_path = "./data/stackoverflow/Posts.xml"

    pairs = {}  # question -> top answer

    for _, post in alive_it(
        ET.iterparse(posts_path), title=f"Reading posts from {posts_path}..."
    ):
        if post.tag != "row":
            continue

        post = dict(post.items())

        post_type = post["PostTypeId"]

        if post_type == "2":
            parent_id = post["ParentId"]

            if parent_id not in pairs:
                pairs[parent_id] = ("", 0)

            score = int(post["Score"])

            if pairs[parent_id][1] < score:
                pairs[parent_id] = (post["Id"], score)

    better_pairs = {}

    for _, post in alive_it(
        ET.iterparse(posts_path), title=f"Reading posts from {posts_path}..."
    ):
        if post.tag != "row":
            continue

        post = dict(post.items())

        if post["Id"] in pairs:
            better_pairs[post["Id"]] = {
                "question_score": int(post["Score"]),
                "answer_id": pairs[post["Id"]][0],
                "answer_score": pairs[post["Id"]][1],
            }

    with open("./data/pairs.json", "w") as f:
        json.dump(better_pairs, f)


# def main():
#     # extract all posts from data dump
#     posts_path = "data/stackoverflow/Posts.xml"
#     posts = {}

#     for _, post in alive_it(
#         ET.iterparse(posts_path), title=f"Reading posts from {posts_path}..."
#     ):
#         if post.tag != "row":
#             continue
#         items = dict(post.items())
#         posts[items["Id"]] = items
#         if len(posts) == 5_000_000:
#             break

#     # get all (question, top answer) pairs
#     question_answers = {}
#     for answer in filter(lambda p: p["PostTypeId"] == "2", posts.values()):
#         question_id = answer["ParentId"]
#         if question_id not in question_answers:
#             question_answers[question_id] = []
#         question_answers[question_id].append(answer)

#     question_answer_pairs = []
#     for question_id, answers in question_answers.items():
#         top_voted_answer = max(answers, key=lambda a: int(a["Score"]))
#         if question_id in posts:
#             question_answer_pairs.append((posts[question_id], top_voted_answer))

#     print(
#         f"Loaded {len(question_answer_pairs)} question-answer pairs ({len(question_answer_pairs)*2} posts) out of {len(posts)} total posts"
#     )

#     pair = random.choice(question_answer_pairs)

#     question_body = pair[0]["Body"]

#     answer_body = pair[1]["Body"]

#     with open("viewer.html", "w") as f:
#         f.write(question_body + "<hr>" + answer_body)

#     print(f"Question ID: {pair[0]['Id']}")
#     print(f"Answer ID: {pair[1]['Id']}")

#     with open("pairs.json", "w") as f:
#         pairs = [
#             {"question": q["Body"], "answer": a["Body"]}
#             for (q, a) in question_answer_pairs
#         ]
#         json.dump(pairs, f)


if __name__ == "__main__":
    main()

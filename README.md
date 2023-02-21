# Stack Overflow GPT
This is the repository for the code for my AP Capstone Research Project

Pseudocode:
```python
pairs = {}

for row in xml file:
    match row type:
        case question:
            # post is a question
            if post id not in pairs:
                # question does not exist
                pairs[post id] = {
                    question score: score
                    number of answers: number of answers
                }
            else:
                # answer was found, but question not found
                pairs[post id][question score] = score
                pairs[post id][number of answers] = number of answers

                # delete entry if all answers have been found
                if pairs[post id][answers seen] >= pairs[post id][number of answers]:
                    append {post id, post score, pairs[post id][answer id]} to file
                    del pairs[post id]
        case answer:
            # post is an answer
            if pairs[parent id] not in pairs:
                # question does not exist
                pairs[parent id] = {
                    answer id: post id,
                    answer score: score,
                    answers seen: 1,
                }
            else:
                # question exists
                if "answer id" not in pairs[post id]:
                    # no answers have been found yet
                    pairs[parent id][answer id] = post id
                    pairs[parent id][answer score] = post score
                    pairs[parent id][answers seen] = 1
                else if answer score > pairs[parent id][answer score]:
                    # at least one answer has been found and a comparison must be made
                    pairs[parent id][answer id] = post id
                    pairs[parent id][answer score] = answer score
                
                # delete entry if all answers have been found
                if pairs[parent id][answers seen] >= pairs[parent id][number of answers]:
                    append {parent id, parent score, post id} to file
                    del pairs[parent id]
                    continue

                # increment number of answers seen
                pairs[parent id][answers seen] += 1
```
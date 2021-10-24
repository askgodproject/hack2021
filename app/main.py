from os.path import realpath
from random import randint
import Utils
from DBPManager import DBPManager
from Passage import Passage, passageKey
from filters import PeopleFilter

question_contexts_full = Utils.readJson(Utils.datasetsPath(realpath(__file__), "Contexts.json", "hack2021"))
scripture_contexts_full = Utils.readJson(Utils.datasetsPath(realpath(__file__), "Scriptures.json", "hack2021"))
question_contexts = question_contexts_full["context"]
scripture_contexts = scripture_contexts_full["scripture"]
scripture_score_map = {}
for scripture_context in scripture_contexts:
    passage_text = scripture_context["passage"]
    scripture_score_map[passage_text] = Passage(passage_text)

# situation_table = {
#     "In conflict with others": {
#         "feeling": [],
#         "concepts": [],
#         "dilema": ""
#     },
#     "Betrayed by a friend" : {

#     }
# }

# Select a question from the given list of questions
# If index is -1, then choose a random question, otherwise use the index if it's valid, otherwise just use 0
def selectQuestion(question_contexts, index = -1):
    # First check if there are any questions
    num = len(question_contexts)
    if num == 0:
        return None
    # Now, grab one at a valid index
    selected_index = index if index >= 0 and index < num else randint(0, num - 1) if index == -1 else 0
    question_context = question_contexts[selected_index]
    return question_context

# ----------
# Main Method
# ----------

# First, get a question
question_context = selectQuestion(question_contexts)
print("Question is: " + question_context["question-text"])

filters = []
filters.append(PeopleFilter(scripture_contexts, scripture_score_map))
for filter in filters:
    filter.process(question_context)

# Determine which verses have the highest scores
# Sort verses in 'current_scripture_contexts' in descending order based on the "score" member
scriptures = sorted(scripture_score_map.values(), key=passageKey, reverse=True)
scripture_to_show = scriptures[0]

print("Answer is: " + scripture_to_show.reference + " - " + scripture_to_show.text())

# Done

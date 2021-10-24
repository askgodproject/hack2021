from os.path import realpath
from random import randint
import nltk
import Utils
from Passage import Passage, passageKey
from filters import *

question_contexts_full = Utils.readJson(Utils.datasetsPath(realpath(__file__), "Contexts.json", "hack2021"))
scripture_contexts_full = Utils.readJson(Utils.datasetsPath(realpath(__file__), "Scriptures.json", "hack2021"))
question_contexts = question_contexts_full["context"]
scripture_contexts = scripture_contexts_full["scripture"]
scripture_score_map = {}
for scripture_context in scripture_contexts:
    passage_text = scripture_context["passage"]
    scripture_score_map[passage_text] = Passage(passage_text)

# TODO Define situation table for the SituationFilter
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

nltk.download('wordnet')

# First, get a question
question_context = selectQuestion(question_contexts)
print("Question is: " + question_context["question-text"])

# Define the filters we'll use
filters = []
filters.append(PeopleFilter(scripture_contexts, scripture_score_map))
filters.append(PlacesFilter(scripture_contexts, scripture_score_map))
filters.append(ActionsFilter(scripture_contexts, scripture_score_map))
filters.append(ScriptureSectionFilter(scripture_contexts, scripture_score_map))
filters.append(QuestionTypeFilter(scripture_contexts, scripture_score_map))

# Go through each filter, which will adjust the scores of the passages in the map
for filter in filters:
    filter.process(question_context)
    scriptures = sorted(scripture_score_map.values(), key=passageKey, reverse=True)

# Now determine which verses have the highest scores
# Sort verses in 'scripture_score_map' in descending order based on the "score" member
scriptures = sorted(scripture_score_map.values(), key=passageKey, reverse=True)
topThreePassagesStr = ""
for i in range(0, 3):
    passage = scriptures[i]
    topThreePassagesStr += passage.reference + " (" + str(passage.score) + ")"
    topThreePassagesStr += "\n" if i < 2 else "" 
print("Top three results:\n" + topThreePassagesStr)
scripture_to_show = scriptures[0]

print("Answer is: " + scripture_to_show.reference + " - " + scripture_to_show.text())

# Done

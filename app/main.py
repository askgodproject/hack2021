import sys
import Utils

question_contexts = Utils.read_json("../Contexts.json");
master_scripture_contexts = Utils.read_json("../Scriptures.json")
situation_table = {
    "In conflict with others": {
        "feeling": [],
        "concepts": [],
        "dilema": ""
    },
    "Betrayed by a friend" : {

    }
}

def selectQuestion(question_contexts):
    # Returns a question from question_contexts
    pass

class Filter:
    def __init__(self):
        pass

    '''
    Given a particular question context, apply filter to it
    return all verses that conform to that filter
    '''
    def process(self, question_context):
        assert False, "Call only on subclasses"

class PeopleFilter(Filter):
    def __init__(self, scripture_contexts):
        super().__init__()
        self.scripture_contexts = scripture_contexts

    def process(self, question_context, ):
        # All people mentioned in this question
        people = question_context["people"]
        # Go through all the scriptures
        for scripture_context in self.scripture_contexts:
            # Go through all the people mentioned in the question
            for person in people:
                # If a person in the question is also in this verse
                # Then increase verse score
                if person in scripture_context["people"]:
                    scripture_context["score"] += 1

# Main Method

question_context = selectQuestion(question_contexts)

# TODO: Deep copy the contexts
current_scripture_contexts = master_scripture_contexts["scripture"]

# Go through all the filters
people_filter = PeopleFilter(current_scripture_contexts)
people_filter.process(question_context)

# Determine which verses have the highest scores
# TODO: Sort verses in 'current_scripture_contexts' in descending order
# based on the "score" member
verses = None
verse_to_show = verses[0]

print(verse_to_show["passage"])

# Done

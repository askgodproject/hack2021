# -----
# Base filter class, should not be instantiated directly
# -----
class Filter:
    def __init__(self, scripture_contexts, scripture_map):
        self.scripture_contexts = scripture_contexts
        self.scripture_map = scripture_map

    '''
    Given a particular question context, apply filter to it
    Adjust score in scripture map of all verses that conform to that filter
    '''
    def process(self, question_context):
        assert False, "Call only on subclasses"

# -----
# People Filter
# Finds all passages which contain the same people as the given question
# -----
class PeopleFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)
    

    def process(self, question_context):
        # All people mentioned in this question
        people = question_context["people"]
        # Go through all the scriptures
        for scripture_context in self.scripture_contexts:
            # Go through all the people mentioned in the question
            for person in people:
                # If a person in the question is also in this verse
                # Then increase verse score
                if person in scripture_context["people"]:
                    passage = self.scripture_map[scripture_context["passage"]]
                    passage.score += 1


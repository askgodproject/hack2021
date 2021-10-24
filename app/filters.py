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
# 1-1 Filter
# Finds all passages which contain at least one of the values in the "key_name" member of the question context
# -----
class OneToOneFilter(Filter):
    def __init__(self, key_name, scripture_contexts, scripture_map):
        self.key_name = key_name;
        self.scripture_contexts = scripture_contexts
        self.scripture_map = scripture_map

    def process(self, question_context):
        # All the key types/entities mentioned in this question (e.g. people, places, etc.)
        keys = question_context[self.key_name]
        # Go through all the scriptures
        for scripture_context in self.scripture_contexts:
            # Go through all the key type/entities mentioned in the question
            for key in keys:
                # If a key in the question is also in this verse, then increase verse score
                if key in scripture_context[self.key_name]:
                    passage = self.scripture_map[scripture_context["passage"]]
                    passage.score += 1

# -----
# People Filter
# Finds all passages which contain the same people as the given question
# -----
class PeopleFilter(OneToOneFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("people", scripture_contexts, scripture_map)

# -----
# Places Filter
# Finds all passages which contain the same places as the given question
# -----
class PlacesFilter(OneToOneFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("places", scripture_contexts, scripture_map)

# -----
# Actions Filter
# Finds all passages which contain the same actions as the given question
# -----
class ActionsFilter(OneToOneFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("actions", scripture_contexts, scripture_map)

# TODO
# -----
# Relating-to Filter
# Finds all passages which relate to the same kind of people/roles/positions as the given question
# Ex. daughters, sons, employers, employees, believers, unbelievers, etc.
# -----
class RelatingToFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)

    
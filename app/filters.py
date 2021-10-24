# -----
# Base filter class, should not be instantiated directly
# -----
class Filter:
    def __init__(self, scripture_contexts, scripture_map):
        self.scripture_contexts = scripture_contexts
        self.scripture_map = scripture_map
        self.sub_filters = []

    '''
    Given a particular question context, apply filter to it
    Adjust score in scripture map of all verses that conform to that filter
    '''
    def process(self, question_context):
        # Default implementation just runs through sub-filters
        for filter in self.sub_filters:
            filter.process(question_context)

# -----
# Simple Comparison Filter
# Scores all passages which have a member whose values appear in a corresponding/similar member in the question context. 
# This could be either a direct/exact comparison of values, or a search for a particular value within the entries of the corresponding member.
# The "question_key_name" is the member of the question context. The "scripture_key_name" is the member in the question context.
# The "only_exact" parameter controls whether we compare values for equality, or if we look for the question key member entries
# within the scripture key member entries.
#
# Example 1: Both questions and scriptures have a "people" array, so we can look in both to see if they contain the same values.
# Both "question_key_name" and "scripture_key_name" equal "people"
# Example 2: Questions contain a list of significant words, and scriptures contain a list of questions the passage can address.
# We can use this filter to search for the significant words in the questions associated with the passage.
# Here, "question_key_name" is "significant-words" and "scripture_key_name" is "questions"
# -----
class SimpleComparisonFilter(Filter):
    def __init__(self, question_key_name, scripture_key_name, only_exact, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)
        self.question_key_name = question_key_name
        self.scripture_key_name = scripture_key_name
        self.only_exact = only_exact
        self.scripture_contexts = scripture_contexts
        self.scripture_map = scripture_map

    def process(self, question_context):
        # All the key types/entities mentioned in this question (e.g. people, places, etc.)
        question_keys = question_context[self.question_key_name]
        # Go through all the scriptures
        for scripture_context in self.scripture_contexts:
            passage = self.scripture_map[scripture_context["passage"]]
            # Go through all the key type/entities mentioned in the question
            for question_key in question_keys:
                # If a key in the question is also in this verse, then increase verse score
                for scripture_key in scripture_context[self.scripture_key_name]:
                    if self.only_exact:
                        if question_key == scripture_key:
                            passage.score += 1
                            print(passage.reference + "(" + str(passage.score) + "): +1 because " + question_key + " == " + scripture_key)
                    else:
                        if question_key in scripture_key:
                            print(passage.reference + "(" + str(passage.score) + "): +1 because " + question_key + " is in " + scripture_key)
                            passage.score += 1
        
        super().process(question_context)

# -----
# People Filter
# Scores all passages which contain the same people as the given question
# -----
class PeopleFilter(SimpleComparisonFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("people", "people", True, scripture_contexts, scripture_map)

# -----
# Places Filter
# Scores all passages which contain the same places as the given question
# -----
class PlacesFilter(SimpleComparisonFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("places", "places", True, scripture_contexts, scripture_map)

# -----
# Actions Filter
# Scores all passages which contain the same actions as the given question
# -----
class ActionsFilter(SimpleComparisonFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("actions", "actions", True, scripture_contexts, scripture_map)

# -----
# Signficant Words Question Filter
# Scores all passages which are associated with questions containing the same significant word(s) as in the given question
# # -----
class QuestionWordsFilter(SimpleComparisonFilter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__("signficant-words", "questions", False, scripture_contexts, scripture_map)

# -----
# Question Comparison Filter
# A combination of the Significant Words Question Filter and the Question Similarity Filter
# -----
class QuestionComparisonFilter(Filter):
    def __init__(self, threshold, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)
        self.sub_filters = [ 
            QuestionWordsFilter(scripture_contexts, scripture_map),
            QuestionSimilarityFilter(threshold, scripture_contexts, scripture_map)
        ]

# -----
# Scripture Section Filter
# Scores passages based on whether they are in the OT or NT, given the Scripture section in the given question
# Note that a question may apply to "Both" or "Neither", but a passage will always be either "OT" or "NT".
# -----
class ScriptureSectionFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)

    def process(self, question_context):
        question_section = question_context["scripture-section"]
        # Go through all the scriptures
        for scripture_context in self.scripture_contexts:
            passage = self.scripture_map[scripture_context["passage"]]
            scripture_section = scripture_context["scripture-section"]
            # If the scripture section is the same as the question section (or the question is for Both)
            # Then increment the score. But if they are for opposite sections, then decrease the score
            # If the question section is Neither, then don't change the score, as it's not applicable
            if scripture_section == "NT" and (question_section == "NT" or question_section == "Both"):
                passage.score += 1
                print(passage.reference + "(" + str(passage.score) + "): +1 " + "because " + scripture_section + " == " + question_section)
            elif scripture_section == "OT" and (question_section == "OT" or question_section == "Both"):
                passage.score += 1
                print(passage.reference + "(" + str(passage.score) + "): +1 " + "because " + scripture_section + " == " + question_section)
            elif (scripture_section == "NT" and question_section == "OT") or \
                 (scripture_section == "OT" and question_section == "NT"):
                passage.score -= 1
                print(passage.reference + "(" + str(passage.score) + "): -1 " + "because " + scripture_section + " != " + question_section)

        super().process(question_context)

# TODO
# -----
# Relating-to Filter
# Scores all passages which relate to the same kind of people/roles/positions as the given question
# Ex. daughters, sons, employers, employees, believers, unbelievers, etc.
# -----
class RelatingToFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)

    def process(self, question_context):
        # TODO
        super().process(question_context)

# TODO
# -----
# Question Similarity Filter
# Does a similarity search on the questions associated with passages, comparing them to the given question;
# Scores all passages which match at or above a given threshold
# -----
class QuestionSimilarityFilter(Filter):
    def __init__(self, threshold, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)
        self.threshold = threshold

    def process(self, question_context):
        # TODO
        # Go through the passages. For every passage, extract its list of associated questions
        # Then run a similarity searching algorithm with input as the list of associated questions, and the new given question
        # The output should be an indication of which associated question the given question is most similar to.
        # That level of similarity is represented by a percentage or other number.
        # If it larger than or equal to the given threshold, we'll score that passage

        self.similarityPrep()
        results = self.runSimilaritySearch(self.textToVector(question_context["question-text"]))

        # TODO Look through the results and only extract those above threshold, then score those passages

        super().process(question_context)

    def runSimilaritySearch(self, question):
        # TODO Use seeded Pinecone model and return the results
        return None

    # TODO: Is this what we really need, is it right?
    def textToVector(self, text_str):
        vector_list = []
        # Convert every character into a numeric representation, and return a list of those numbers
        for character in text_str:
            vector_list.append(int(character))
        return vector_list

    def similarityPrep(self):
        # Make array of pairs, each pair being a question, and its associated passage
        association_list = []
        for scripture in self.scripture_contexts:
            associated_questions = scripture["questions"]
            for question in associated_questions:
                association_list.append((scripture["passage"], question))
        
        # TODO Transform list of pairs into a vector of numerical data that can seed the similarity algorithm
        # TODO Seed the Pinecone algorithm with this data and save as a member variable

# TODO
# -----
# Question Type Filter
# Scores all passages which have a question type that matches to the question type of the given question
# -----
class QuestionTypeFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)

    def process(self, question_context):
        # TODO
        # Go through all the passages and extract the "question-type" objects
        # Then compare those to the given question. If they "match" then score that passage.
        # Determining a "match" could mean they have the exact same values for the different members of a question type
        # or it could mean they are close enough. For example, the entry "gay" and entry "homosexual" are probably close
        # enough to match, at least for those elements.

        super().process(question_context)

# TODO
# -----
# Situation Filter
# Converts the given question's details to a "situation" and scores all passages whose "lessons" match to that situation.
# The given map of situations is used to compare the representation of a "situation" in the question with the known
# representations of "situations" contained in the map, and we'll use the titles of the ones which match close enough,
# to look for passages which can help address those situations
# -----
class SituationFilter(Filter):
    def __init__(self, situation_map, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)
        self.situation_map = situation_map

    def process(self, question_context):
        # TODO
        # A situation is represented by a combination of "feelings," "concepts," and "dilemas". This is how they are
        # represented in the given map, and we want to convert the given question to the same format, so we can compare them.
        # To determine these elements, one possible way is to map:
        #  - "emotions" and "preconceptions" to "feelings"
        #  - "significant-words" and "actions" to "concepts"
        #  - "question-types" to "dilemas"
        # When comparing the resulting "situation" with those in the "lessons" of the passages, we'll first collect those
        # passages which have matching situations in their lessons. Then we'll see if those lessons relates to believers, 
        # or not. If passage does, but the question does not, or vice versa, then we'll score that passage lower, 
        # and we'll score it higher if they are the same (either both for believers, or both for unbelievers).
        # This is assuming the believer info is provided.

        super().process(question_context)

# TODO
# -----
# Verse in Question Filter
# If the question contains a Scripture reference, then it's highly likely that we should return that verse for them.
# So if we have that verse in our index, we should score it higher. A consideration though here is that we probably
# want to return at least 2 verses to the user in this case, because just returning the verse they are asking about
# is quite probably not helpful to them; they probably know it already.
#
# One way to enhance this would be on the initial question processing, when we're creating the question context,
# to see if phrases from Scriptures are included, and not just Scripture references. That is another way to reference
# a passage, by quoting the text, and should be recognized as well
# -----
class VerseInQuestionFilter(Filter):
    def __init__(self, scripture_contexts, scripture_map):
        super().__init__(scripture_contexts, scripture_map)

    def process(self, question_context):
        # TODO Search for that verse in the index

        super().process(question_context)

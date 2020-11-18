# Name of File: part_of_speech_tags_key.py
# Date: November 18th, 2020
# Purpose of File: to make a key of the part of speech abbreviations returned by textblob
import numpy as np
import pandas as pd

specific_pos_columns = ["abbreviation", "part_of_speech", "definition"]

# Parts of speech specified by the NLTK library
# https://pythonprogramming.net/natural-language-toolkit-nltk-part-speech-tagging/
# I am not filling in the definition right now - instead categorizing them into broader
# groups and giving the definitions for the broader groups
specific_pos = [["CC", "coordinating conjunction", ""],
 ["CD", "cardinal digit", ""],
 ["DT", "determiner", ""],
 ["EX", "existential 'there' (example: 'there' is)", ""],
 ["FW", "foreign word", ""],
 ["IN", "preposition/subordinating conjunction", ""],
 ["JJ", "adjective (example: big)", ""],
 ["JJR", "comparative adjective (example: bigger)", ""],
 ["JJS", "superlative adjective (example: biggest)", ""],
 ["LS", "list marker (example: 1)", ""],
 ["MD", "modal (example: could, will)", ""],
 ["NN", "singular noun (example: desk)", ""],
 ["NNS", "plural noun (example: desks)", ""],
 ["NNP", "singular proper noun (example: Harrison)", ""],
 ["NNPS", "plural proper noun (example: Americans)", ""],
 ["PDT", "predeterminer (example: all the kids)", ""],
 ["POS", "possessive ending (example: parent's)", ""],
 ["PRP", "personal pronoun (example: I, he, she)", ""],
 ["PRP$", "possessive pronoun (example: my, his, hers)", ""],
 ["RB", "adverb (example: very, silently)", ""],
 ["RBR", "comparative adverb (example: better)", ""],
 ["RBS", "superlative adverb (example: best)", ""],
 ["RP", "particle (example: give up)", ""],
 ["TO", "to go (example: 'to' the store)", ""],
 ["UH", "interjection (example: errrm)", ""],
 ["VB", "verb, base form (example: take)", ""],
 ["VBD", "verb, past tense (example: took)", ""],
 ["VBG", "verb, gerund/present participle (example: taking)", ""],
 ["VBN", "verb, past participle (example: taken)", ""],
 ["VBP", "verb, singular present, non-3d (example: take)", ""],
 ["VBZ", "verb, 3rd person singular present (example: takes)", ""],
 ["WDT", "wh-determiner (example: which)", ""],
 ["WP", "wh-pronoun (example: who, what)", ""],
 ["WP$", "possessive wh-pronoun (example: whose)", ""],
 ["WRB", "wh-abverb (example: where, when)", ""]
]
specific_pos_df = pd.DataFrame(specific_pos, columns = specific_pos_columns)
specific_pos_df.to_csv("specific_parts_of_speech_key.csv")

# Broader Parts of Speech 
# https://www.englishclub.com/grammar/parts-of-speech.htm
# Definitions from https://www.thoughtco.com/part-of-speech-english-grammar-1691590
broad_pos_columns = ["abbreviation", "part_of_speech", "specific_pos", "definition"]
broad_pos = [["N", "Noun", ["NN", "NNS", "NNP", "NNPS"], "a person, place, or thing"],
 ["PRON", "Pronoun", ["PRP", "PRP$"], "stands in for a noun in a sentence"],
 ["V", "Verb", ["MD", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"], "words that show action or a state of being"],
 ["ADJ", "Adjective", ["JJ", "JJR", "JJS"], "describe nouns and pronouns"],
 ["ADV", "Adverb", ["RB", "RBR", "RBS"], "describe verbs, adjectives, or other adjectives"],
 ["DET", "Determiner", ["CD", "DT", "PDT"], "function like adjectives by modifying nouns, but are different than adjectives because they are needed for a sentence to have proper syntax"],
 ["PREP", "Preposition", ["IN"], "show spacial, temporal, and role relations between a noun or pronoun and the other words in a sentence"],
 ["CONJ", "Conjunction", ["CC"], "join words, phrases, and clauses in a sentence"],
 ["INT", "Interjection", ["UH"], "an exclamation"],
 ["OTH", "Other", ["EX", "FW", "LS", "POS", "RP", "TO", "WDT", "WP", "WP$", "WRB"], "not one of the primary nine parts of speech"],
 ["MULT", "Multiple", [], "multiple parts of speech"]
]
broad_pos_df = pd.DataFrame(broad_pos, columns = broad_pos_columns)
# Save as a csv file
broad_pos_df.to_csv("broad_parts_of_speech_key.csv")


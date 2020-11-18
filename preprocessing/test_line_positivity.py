# Name of File: line_positivity.py
# Date: November 18th, 2020
# Purpose of File: to test whether the HuggingFace API gets a different
#                  result when punctuation is included
# Tools used:
# HuggingFace Library (https://huggingface.co/transformers/quicktour.html)
from transformers import pipeline

# Used for the HuggingFace Library (see https://huggingface.co/transformers/quicktour.html)
# This sentiment-analysis classifier "uses the DistilBERT architecture and has been 
# fine-tuned on a dataset called SST-2 for the sentiment analysis task."
# model_name = "distilbert-base-uncased-finetuned-sst-2-english"
hugface_classifier = pipeline('sentiment-analysis')

print("===============================================")
# Testing what happens if one word changes and nothing else does (ta->to here)
line_1 = "Took a hour just ta get the car seat in right"
hugface_sentiment_1 = hugface_classifier(line_1)
hugface_label_1 = hugface_sentiment_1[0]["label"]
hugface_score_1 = round(hugface_sentiment_1[0]["score"], 4)
print("line = ", line_1, ", label = ", hugface_label_1, ", score = ", hugface_score_1)
# Result: line =  Took a hour just ta get the car seat in right  label =  NEGATIVE  score =  0.996

line_2 = "Took a hour just to get the car seat in right"
hugface_sentiment_2 = hugface_classifier(line_2)
hugface_label_2 = hugface_sentiment_2[0]["label"]
hugface_score_2 = round(hugface_sentiment_2[0]["score"], 4)
print("line = ", line_2, ", label = ", hugface_label_2, ", score = ", hugface_score_2)
# Result: line =  Took a hour just to get the car seat in right  label =  NEGATIVE  score =  0.9973 

print("===============================================")
# Testing what happens if punctuation is removed
line_3 = "A general, a doctor, maybe a MC"
hugface_sentiment_3 = hugface_classifier(line_3)
hugface_label_3 = hugface_sentiment_3[0]["label"]
hugface_score_3 = round(hugface_sentiment_3[0]["score"], 4)
print("line = ", line_3, ", label = ", hugface_label_3, ", score = ", hugface_score_3)
# Result: line =  A general, a doctor, maybe a MC , label =  POSITIVE , score =  0.8229

line_4 = "A general a doctor maybe a MC"
hugface_sentiment_4 = hugface_classifier(line_4)
hugface_label_4 = hugface_sentiment_4[0]["label"]
hugface_score_4 = round(hugface_sentiment_4[0]["score"], 4)
print("line = ", line_4, ", label = ", hugface_label_4, ", score = ", hugface_score_4)
# Result: line =  A general a doctor maybe a MC , label =  POSITIVE , score =  0.8319

print("===============================================")
# Testing the combined affect (remove punctuation, change a word, and then do both)
line_5 = "Five years old, bringin comedy"
hugface_sentiment_5 = hugface_classifier(line_5)
hugface_label_5 = hugface_sentiment_5[0]["label"]
hugface_score_5 = round(hugface_sentiment_5[0]["score"], 4)
print("line = ", line_5, ", label = ", hugface_label_5, ", score = ", hugface_score_5)
# Result: line =  Five years old, bringin comedy , label =  POSITIVE , score =  0.9965

line_6 = "Five years old bringin comedy"
hugface_sentiment_6 = hugface_classifier(line_6)
hugface_label_6 = hugface_sentiment_6[0]["label"]
hugface_score_6 = round(hugface_sentiment_6[0]["score"], 4)
print("line = ", line_6, ", label = ", hugface_label_6, ", score = ", hugface_score_6)
# Result: line =  Five years old bringin comedy , label =  POSITIVE , score =  0.9847

line_7 = "Five years old, bringing comedy"
hugface_sentiment_7 = hugface_classifier(line_7)
hugface_label_7 = hugface_sentiment_7[0]["label"]
hugface_score_7 = round(hugface_sentiment_7[0]["score"], 4)
print("line = ", line_7, ", label = ", hugface_label_7, ", score = ", hugface_score_7)
# Result: line =  Five years old, bringing comedy , label =  POSITIVE , score =  0.9998

line_8 = "Five years old bringing comedy"
hugface_sentiment_8 = hugface_classifier(line_8)
hugface_label_8 = hugface_sentiment_8[0]["label"]
hugface_score_8 = round(hugface_sentiment_8[0]["score"], 4)
print("line = ", line_8, ", label = ", hugface_label_8, ", score = ", hugface_score_8)
# Result: line =  Five years old bringing comedy , label =  POSITIVE , score =  0.9998

# My analysis is that removing words and replacing punctuation can both have the effect of making the score closer to 1
# I am going to construct the sentences that will be classified by removing all punctuation and using the 'words_can_search'
# versions of words. This decision can be changed later.  
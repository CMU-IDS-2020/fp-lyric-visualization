# Name of File: dictionary_preprocess.py
# Date: November 14th, 2020
# Purpose of File: Test usage of Merriam-Webster api by looking up the
# 					word 'test' in the dictionary and the thesaurus
# 					and writing the output to individual files
# Tools used:
# Merriam-Webster (https://dictionaryapi.com/)
import urllib.request as ur
import json

# Used for the Merriam-Webster API
# keys are obfuscated here because they are associated with an account
# CAUTION: insert own keys for dict_key and thes_key
word = "test"
dict_url = "https://dictionaryapi.com/api/v3/references/collegiate/json/"
dict_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
thes_url = "https://dictionaryapi.com/api/v3/references/thesaurus/json/"
thes_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# from https://www.powercms.in/article/how-get-json-data-remote-url-python-script
# and https://stackoverflow.com/questions/3969726/attributeerror-module-object-has-no-attribute-urlopen
dict_file = open("test_m_w_dictionary.json", "w")
json_dict_url = ur.urlopen(dict_url + word + "?key=" + dict_key)
dict_data = json.loads(json_dict_url.read())
dict_file.write(json.dumps(dict_data))
dict_file.close()

thes_file = open("test_m_w_thesaurus.json", "w")
json_thes_url = ur.urlopen(thes_url + word + "?key=" + thes_key)
thes_data = json.loads(json_thes_url.read())
thes_file.write(json.dumps(thes_data))
thes_file.close()



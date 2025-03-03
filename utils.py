from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk import word_tokenize

import json
import sys

def print_question(prompt, possible_options = []):
    print(prompt)
    if not len(possible_options) == 0:
      print("Options:", ", ".join(possible_options))

def initialize_available_options(house_data, available_options):
    for house in house_data['houses']:
        for key, value in house.items():
            available_options.setdefault(key, set()).add(value)

def preprocess_answer(answer):
    answer = word_tokenize(answer)
    return answer

def get_numerical_value(tok_answer):
    for token in tok_answer:
        if token.isnumeric() or token[:-1].isnumeric():
            return token
    return ''

def convert_into_num(num):
    if num[-1].lower() == 'k':
        num = float(num[:-1]) * 1000
    return int(num)

def print_suitable_houses(suitable_houses):
    if suitable_houses:
        print("\nBased on your preferences, the most suitable houses are:")
        for house in suitable_houses:
            print(f"House ID: {house['id']}")
            print(f"Type: {house['type']}")
            print("Bedrooms:", house['bedrooms'])
            print("Bathrooms:", house['bathrooms'])
            print("Price:", house['price'], "euros")
            print("Square Meters:", house['square_meters'], "m^2")
            print("Floor:", house['floor'], "º")
            print("Elevator:", house['elevator'])
            print("Commercial Use:", house['commercial_use'])
            print("Terrace:", house['terrace'])
            print("Location:", house['location'])
            print()
    else:
        print("\nSorry, no suitable houses match your preferences. \n")

def extract_range(oracion):
    #Precondició: l'oració ha de contenir 2 números que representen un rang.
    tokens = preprocess_answer(oracion)
    numeros = [int(convert_into_num(token)) for token in tokens if token.isnumeric() or token[:-1].isnumeric()]
    return range(numeros[0], numeros[1]+1)

def extract_answers(oracion, options):
    #Precondició: S'espera que l'oració contingui les opcions, sinó retorna un conjunt buit
    answer= set()
    oracion_set = preprocess_answer(oracion)

    for option in options:
      option_set = set(option.split())

      if option_set.issubset(oracion_set):
        answer = answer.union(set([option]))
    return answer

def convert_into_bool(string):
    if string.lower() == 'yes':
        return True
    elif string.lower() == 'no':
        return False
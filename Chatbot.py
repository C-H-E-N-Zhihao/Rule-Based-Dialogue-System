from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer

import json
import sys

from utils import *

class Chatbot():
      def __init__(self, data):
          self.data = data
          self.available_options = {}
          initialize_available_options(data, self.available_options)
          self.filters = {
                'type': lambda answer, house: house in answer,
                'bedrooms': lambda answer, house: int(house) >= int(answer),
                'bathrooms': lambda answer, house: int(house) >= int(answer),
                'price':lambda answer, house: convert_into_num(house) <= convert_into_num(answer) and \
                                                (convert_into_num(house) <= convert_into_num(self.user_preferences['income'])*0.35 \
                                                if self.house_type == 'rent' else True),
                'square_meters': lambda answer, house: int(house) >= int(answer),
                'floor': lambda answer, house: int(house) >= int(answer),
                'elevator': lambda answer, house: house in answer or "No" in answer,
                'commercial_use': lambda answer, house: house in answer or "No" in answer,
                'terrace': lambda answer, house: house in answer or "No" in answer,
                'location': lambda answer, house: house in answer
                }
          self.any = []

      def init(self):
          self.user_preferences = {}
          print(self.data['start_message'])
          print('For each question, I am going to offer you the available options.')
          print('Ensure that your answer is short and clear, please!')
          print('You can always answer QUIT to quit the conversation or ANY to include all possibilities.')

          for question in self.data['questions']:
            answer_key = question['answer_key']
            if (answer_key != 'income'):
                possible_options = list(self.available_options.get(answer_key))

            if question['type'] == 'numerical':
                if (answer_key != 'income') or \
                (answer_key == 'income' and self.user_preferences['type'] != 'sale' ):
                    answer = self.process_numerical_question(question)

                if answer_key == 'price' and self.user_preferences['type'] != 'sale' and 'income' not in self.any:
                    rich = False
                    while not rich and convert_into_num(answer) > convert_into_num(self.user_preferences['income'])*0.35:
                        print('We recommend that you do not spend more than 35% of your monthly income on rent.')
                        rich = convert_into_bool(input('Are you sure you can keep the same budget? (Enter Yes or No)'))
                        if rich == None:
                            rich = False
                            print('You are not giving any of the available options, please ensure that your answer does not have any mistake.')
                        elif not rich:
                            answer = self.process_numerical_question(question)
                        else:
                            self.filters['price'] = lambda answer, house: convert_into_num(house) <= convert_into_num(answer)

            else:
                answer = self.process_multichoice_question(question, possible_options)

            self.user_preferences[answer_key] = answer

          self.find_suitable_houses()
          print_suitable_houses(self.suitable_houses)

          print(self.data['end_message'])

      def process_numerical_question(self, question):
          print_question(question['question'])
          while True:
            answer = input(question['prompt'])
            range = extract_range(question['prompt'])
            # Poder finalitzar el programa
            if answer.lower() == 'quit':
                print(self.data['end_message'])
                sys.exit()
            # Opció de respondre any
            elif answer.lower() == 'any':
                self.any.append(question['answer_key'])
                return None
            else:
                tok_answer = preprocess_answer(answer)
                value = get_numerical_value(tok_answer)
                if value == '':
                    print('You are not introducing any numerical number, please ensure that your answer does not have any mistake.')
                elif convert_into_num(value) in range:
                    return value
                elif convert_into_num(value) not in range:
                    print('Your answer is out of range, please ensure that your answer does not have any mistake.')

      def process_multichoice_question(self, question, options):
          print_question(question['question'], options)
          while True:
            answer = input(question['prompt'])
            # Poder finalitzar el programa
            if answer.lower()  == 'quit':
                print(self.data['end_message'])
                sys.exit()
            # Opció de respondre any
            elif answer.lower() == 'any':
                self.any.append(question['answer_key'])
                return None
            elif len(extract_answers(answer, options)) > 0:
                return extract_answers(answer, options)
            else:
                print('You are not giving any of the available options, please ensure that your answer does not have any mistake.')

      def find_suitable_houses(self):
          self.suitable_houses = []
          for house in self.data['houses']:
            self.house_type = house['type']
            # Filtrar les keys que estiguin en la llista de any o que compleixin el filtre
            if all((key in self.any or self.filters[key](self.user_preferences[key], house[key])) for key in self.user_preferences if key in self.filters):
              filtered_house_info = house
              self.suitable_houses.append(filtered_house_info)

if __name__ == '__main__':
    with open('D:/Zhihao Chen/GIA/3r_1/TVD/LAB/P1/dades/house_data_new.json') as f:
        new_data = json.load(f)
    user = Chatbot(new_data)
    user.init()
    print(user.user_preferences)
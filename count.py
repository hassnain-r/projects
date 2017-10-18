from __future__ import division
import json
import glob
import argparse


class JsonAnalyzer:
    def __init__(self, name='jsonanalyzer'):
        self.name = name

    def countdata(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--filename')
        args = parser.parse_args()
        with open(args.filename, 'r') as my_file:
            content = json.load(my_file)
            config = len(content)
            string = 'Total_Rows'
            print('{} {}'.format(string, config))
            dictionary = {}
            for row in content:
                for field in row:
                    if row[field]:
                        if dictionary.get(field):
                            dictionary[field]['count'] += 1
                            dictionary[field]['type'] = type(row[field]).__name__
                        else:
                            dictionary[field] = {}
                            dictionary[field]['count'] = 1
                            dictionary[field]['type'] = None
            for field in dictionary:
                value_in_percentage = dictionary[field]['count']/config * (100)
                final_data = str(field) + ': ' + str(dictionary[field]['type']) + '[' + str(value_in_percentage) + '%' + ']'
                print (final_data)

    def unique_data(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--category')
        args = parser.parse_args()
        with open(args.category, 'r') as file_:
            content = json.load(file_)
            total_rows = len(content)
            print ('{} = {}'.format('Total_Rows', total_rows))
            sorted_element = []
            for element in content:
                try:
                    sorted_element.append(sorted(element["speciality"]))
                except:
                    pass
            type_of_field = type(sorted_element[0]).__name__
            percentage = len(sorted_element) / total_rows * 100
            category = str(type_of_field) + ':' + '[' + str(percentage) + '%' ']'
            print (category)

if __name__ == '__main__':
    s = JsonAnalyzer()
    parsers = argparse.ArgumentParser()
    parsers.add_argument('-f', '--filename')
    parsers.add_argument('-c', '--category')
    args1 = parsers.parse_args()
    if args1.filename:
        print(s.countdata())
    elif args1.category:
        print(s.unique_data())
    else:
        print 'program ends'




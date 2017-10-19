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
        result = []
        with open(args.category, 'r') as json_file:
            dic = json.load(json_file)
            for item in dic:
                dictionary = {}
                for key in item:
                    if type(item[key]) is list:
                        for sub_item in item[key]:
                            if type(sub_item) is dict:
                                dictionary[key] = {}
                                for sub_item_key in sub_item:
                                    if type(sub_item[sub_item_key]) is list:
                                        dictionary[key][sub_item_key] = sub_item[sub_item_key][0]
                                    else:
                                        dictionary[key][sub_item_key] = sub_item[sub_item_key]
                            else:
                                dictionary[key] = sub_item
                    else:
                        dictionary[key] = item[key]
                result.append(dictionary)
        list_with_values = []
        for key in result:
            print key['speciality']['name']
            list_with_values.append(key['speciality']['name'])
        type_of_field = type(list_with_values[0]).__name__
        actual_length = len(sorted(set(list_with_values)))
        total_length = len(list_with_values)
        percentage = actual_length / total_length * 100
        _str = "% unique"
        print ('{}:[{}{}]'.format(type_of_field, percentage, _str))


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




from __future__ import division
import json
import argparse


class JsonAnalyzer:
    def __init__(self, name='jsonanalyzer'):
        self.name = name

    def countdata(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f_n', '--filename')
        args = parser.parse_args()
        with open(args.filename, 'r') as my_file:
            content = json.load(my_file)
            config = len(content)
            string = 'Total_Rows'
            print('{} {}'.format(string, config))

            def get_recursion(json_items, result=None, parent_key=None):

                if result is None:
                    result = {}
                if isinstance(json_items, dict):
                    for dict_key, dict_value in json_items.items():
                        if parent_key:
                            result_key = parent_key + '.' + dict_key
                        else:
                            result_key = dict_key
                        if result_key not in result:
                            result[result_key] = {}
                        if "unique" not in result[result_key]:
                            result[result_key]["unique"] = []
                        if "type" not in result[result_key]:
                            result[result_key]["type"] = ""
                        if "count" not in result[result_key]:
                            result[result_key]["count"] = 0
                        result[result_key]["type"] = type(dict_value).__name__
                        if isinstance(dict_value, int):
                            if dict_value != 0:
                                result[result_key]["count"] += 1
                        elif len(dict_value) > 0:
                            result[result_key]["count"] += 1
                        result = get_recursion(dict_value, result, dict_key)
                if isinstance(json_items, list):
                    for value in json_items:
                        result = get_recursion(value, result, parent_key)
                return result

            new_data = get_recursion(content)
            for final_key, final_value in new_data.items():
                percentage = final_value['count'] / len(content) * 100
                type_of_element = (final_value['type'])
                print (final_key + " = " + str(type_of_element) + "[" + str(percentage) + "]")

    def unique_data(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--single_category')
        parser.add_argument('-f', '--file_name')
        args = parser.parse_args()
        args.single_category = ''
        with open(args.file_name, 'r') as my_file:
            content = json.load(my_file)
            config = len(content)
            string = 'Total_Rows'
            print('{} {}'.format(string, config))

            def get_recursion(json_items, result=None, parent_key=None):

                if result is None:
                    result = {}
                if isinstance(json_items, dict):
                    for dict_key, dict_value in json_items.items():
                        if parent_key:
                            result_key = parent_key + '.' + dict_key
                        else:
                            result_key = dict_key
                        if result_key not in result:
                            result[result_key] = {}
                        if "unique" not in result[result_key]:
                            result[result_key]["unique"] = []
                        if "type" not in result[result_key]:
                            result[result_key]["type"] = ""
                        if "count" not in result[result_key]:
                            result[result_key]["count"] = 0
                        result[result_key]["type"] = type(dict_value).__name__
                        if isinstance(dict_value, int):
                            if dict_value != 0:
                                result[result_key]["count"] += 1
                        elif len(dict_value) > 0:
                            result[result_key]["count"] += 1
                        if dict_value and dict_value not in result[result_key]["unique"]:
                            result[result_key]["unique"].append(dict_value)
                        result = get_recursion(dict_value, result, dict_key)

                if isinstance(json_items, list):
                    for value in json_items:
                        result = get_recursion(value, result, parent_key)
                return result

            new_data = get_recursion(content)
            for final_key, final_value in new_data.items():
                if args1.single_category == final_key:
                    type_of_data = final_value['type']
                    original_count = len(final_value['unique'])
                    total_count = (final_value['count'])
                    percentage = original_count / total_count * 100
                    print (final_key + " = " + str(type_of_data) + '[' + str(percentage) + '% unique]' + str(final_value['unique']))

if __name__ == '__main__':
    s = JsonAnalyzer()
    parsers = argparse.ArgumentParser()
    parsers.add_argument('-c', '--single_category')
    parsers.add_argument('-f', '--file_name')
    parsers.add_argument('-f_n', '--filename')
    args1 = parsers.parse_args()
    if args1.single_category:
        if args1.file_name:
            print (s.unique_data())
    elif args1.filename:
        print (s.countdata())

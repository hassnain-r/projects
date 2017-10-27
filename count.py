from __future__ import division
import json
import argparse


class JsonAnalyzer(object):
    def unique_values_and_type(self, is_category=False):
        with open(args.filename)as my_file:
            content = json.load(my_file)
            print('{} {}'.format('Total_Rows', len(content)))

            def nested_dict_iterator(json_items, result=None, parent_key=None):  # recursive func for nested dicts
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

                        if "type" not in result[result_key]:
                            result[result_key]["type"] = ""
                        result[result_key]["type"] = type(dict_value).__name__
                        if is_category:
                            if "unique" not in result[result_key]:
                                result[result_key]["unique"] = []
                            if dict_value and dict_value not in result[result_key]["unique"]:
                                result[result_key]["unique"].append(dict_value)

                        if "count" not in result[result_key]:
                            result[result_key]["count"] = 0

                        if isinstance(dict_value, int):
                            if dict_value != 0:
                                result[result_key]["count"] += 1
                        elif len(dict_value) > 0:
                            result[result_key]["count"] += 1
                        result = nested_dict_iterator(dict_value, result, dict_key)

                elif isinstance(json_items, list):
                    for value in json_items:
                        result = nested_dict_iterator(value, result, parent_key)
                return result
            new_data = nested_dict_iterator(content)

            if is_category:
                self.final_result_unique_category(new_data)
            else:
                self.final_result_all_categories(new_data, len(content))

    def final_result_unique_category(self, final_data):
        
        for final_key, final_value in final_data.items():
            if args.each_category == final_key:
                type_of_data = final_value['type']
                original_count = len(final_value['unique'])
                total_count = (final_value['count'])
                percentage = original_count / total_count * 100
                print (final_key + " = " + str(type_of_data) + '[' + str(percentage) + '% unique]' + "\n"
                       + str(sorted(final_value['unique'])))

    def final_result_all_categories(self, final_data, content_length):
        for final_key, final_value in final_data.items():
            percentage = final_value['count'] / content_length * 100
            type_of_element = (final_value['type'])
            print (final_key + " = " + str(type_of_element) + "[" + str(percentage) + "]")

if __name__ == '__main__':
    my_class = JsonAnalyzer()
    parsers = argparse.ArgumentParser()
    parsers.add_argument('-f', '--filename')
    parsers.add_argument('-c', '--each_category')
    args = parsers.parse_args()
    if args.each_category:
        if args.filename:
            print (my_class.unique_values_and_type(True))
    elif args.filename:
        print (my_class.unique_values_and_type(False))




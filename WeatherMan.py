import csv
import glob
import operator
import argparse
import termcol


class WeatherMan:
    def __init__(self, name='weatherman'):
        self.name = name

    def weather_man(self):
        dic = {'max_temp': {}, 'min_temp': {}, 'max_hum': {}}
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', help='it will lead you to all the files by providing path')
        parser.add_argument('-e', '--year', help='by providing year you will get data of that particular year')
        args = parser.parse_args()

        path = glob.glob(args.path)
        for files in path:
            if files.find(args.year) > 0:
                open_files = open(files)
                next(open_files)
                dict_version = csv.DictReader(open_files, delimiter=',')
                for fetching_data in dict_version:
                    mx_temp_key = fetching_data['Max TemperatureC']
                    if mx_temp_key:
                        mn_temp_key = fetching_data['Min TemperatureC']
                        if mn_temp_key:
                            mx_humi_key = fetching_data['Max Humidity']
                            if mx_humi_key:
                                pkt = fetching_data.get('PKT') or fetching_data.get('PKST')
                                if pkt:
                                    dic['max_temp'][pkt] = int(mx_temp_key)
                                    dic['min_temp'][pkt] = int(mn_temp_key)
                                    dic['max_hum'][pkt] = int(mx_humi_key)

        sorting_max_tem = sorted(dic['max_temp'].items(), key=operator.itemgetter(1))
        sort = sorting_max_tem[-1]
        print('{}:{}C on {}'.format('Highest', sort[1], sort[0]))
        sorting_min_tem = sorted(dic['min_temp'].items(), key=operator.itemgetter(1))
        a = sorting_min_tem[0]
        print('{}:{}C on {}'.format('Lowest', a[1], a[0]))
        sorting_max_hum = sorted(dic['max_hum'].items(), key=operator.itemgetter(1))
        b = sorting_max_hum[-1]
        print('{}:{}% on {}'.format('Humid', b[1], b[0]))

    def average_value(self):
        list1 = []
        list2 = []
        list3 = []
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', help='path will lead us to all files')
        parser.add_argument('-a', '--month', help='file of particular month')
        args = parser.parse_args()
        path = glob.glob(args.path)
        for files in path:
            if files.find(args.month) > 0:
                open_file = open(files)
                next(open_file)
                dic = csv.DictReader(open_file, delimiter=',')
                for fetching_data in dic:
                    a = fetching_data['Max TemperatureC']
                    if a:
                        list1.append(int(a))
                        b = fetching_data['Min TemperatureC']
                        if b:
                            list2.append(int(b))
                            c = fetching_data['Max Humidity']
                            if c:
                                list3.append(int(c))
        max__tem_ave = (sum(list1)) / (len(list1))
        print'{} :{}C'.format('Highest Average', max__tem_ave)
        min__tem_ave = (sum(list2)) / (len(list2))
        print'{} :{}C'.format('Lowest Average', min__tem_ave)
        max__hum_ave = (sum(list3)) / (len(list3))
        print'{} :{}%'.format('Average Humidity', max__hum_ave)

    def bar_chart(self):
        dic = {'max_temp': {}, 'min_temp': {}}
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', '--path', help='it will lead you to all the files by providing path')
        parser.add_argument('-c', '--mahina', help='by providing year you will get data of that particular year')
        args = parser.parse_args()
        path = glob.glob(args.path)
        for files in path:
            if files.find(args.mahina) > 0:
                open_files = open(files)
                next(open_files)
                dict_version = csv.DictReader(open_files, delimiter=',')
                for fetching_data in dict_version:
                    mx_temp_key = fetching_data['Max TemperatureC']
                    if mx_temp_key:
                        mn_temp_key = fetching_data['Min TemperatureC']
                        if mn_temp_key:
                            pkt = fetching_data.get('PKT') or fetching_data.get('PKST')
                            if pkt:
                                dic['max_temp'][pkt] = int(mx_temp_key)
                                dic['min_temp'][pkt] = int(mn_temp_key)

        a = sorted(dic['max_temp'].items(), key=operator.itemgetter(1))
        b = sorted(dic['min_temp'].items(), key=operator.itemgetter(1))
        for (i, p) in zip(a, b):
            c = i[0]
            d = i[1]
            string1 = '-'
            string1 = string1.replace('-', termcolor.colored(d * '+', 'red'))
            print('{}:{}:{}C'.format(c, string1, d))
            f = p[1]
            string2 = '-'
            string2 = string2.replace('-', termcolor.colored(f * '+', 'blue'))
            print('{}:{}:{}C'.format(c, string2, f))

if __name__ == '__main__':
    s = WeatherMan()
    parsers = argparse.ArgumentParser()
    parsers.add_argument('-p', '--path', help='path will lead us to all files')
    parsers.add_argument('-a', '--month', help='file of particular month')
    parsers.add_argument('-e', '--year', help='by providing year you will get data of that particular year')
    parsers.add_argument('-c', '--mahina', help='by providing year you will get data of that particular year')
    args1 = parsers.parse_args()
    if args1.month:
        print(s.average_value())
    elif args1.year:
        print(s.weather_man())
    elif args1.mahina:
        print(s.bar_chart())
    else:
        print('please select a valid parameter')


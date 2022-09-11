import csv
import os

headers = ['date', 'total_resto', 'total_delivery', 'total']


def write_daily_zvit(data, env):
    if env == 'prod':
        filename = '/home/user/wa_history.csv'
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', encoding='UTF8') as f:
            writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)

            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header

            data = dict(zip(headers, data))
            writer.writerow(data)
    else:
        filename = 'wa_history.csv'
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', encoding='UTF8') as f:
            writer = csv.DictWriter(f, delimiter=',', lineterminator='\n', fieldnames=headers)

            if not file_exists:
                writer.writeheader()  # file doesn't exist yet, write a header

            data = dict(zip(headers, data))
            writer.writerow(data)

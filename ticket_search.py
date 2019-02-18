import csv
import re
from pymongo import MongoClient
import pymongo
from pprint import pprint
from datetime import datetime


client = MongoClient()
tickets_db = client.tickets


def read_data(csv_file, db):
    """
    Загрузить данные в бд из CSV-файла
    """
    with open(csv_file, encoding='utf8') as csvfile:
        # прочитать файл с данными и записать в коллекцию
        reader = csv.DictReader(csvfile)
        ticket_data = list()
        for row in reader:
            row['Цена'] = int(row['Цена'])
            date_str = row['Дата'] + '.{}'.format(datetime.now().year)
            row['Дата'] = datetime.strptime(date_str, '%d.%m.%Y').date()
            ticket_data.append(row)
        # создаем коллекцию билетов
        tickets_list = db.tickets_list
        tickets_list.insert_many(ticket_data)


def find_cheapest(db):
    """
    Найти самые дешевые билеты
    Документация: https://docs.mongodb.com/manual/reference/operator/aggregation/sort/
    """
    sorted_tickets = list(db.tickets_list.find().sort('Цена', pymongo.ASCENDING))
    print('Самый дешевый билет на концерт {} стоит {}'.format(sorted_tickets[0]['Исполнитель'],
                                                              sorted_tickets[0]['Цена']))


def find_by_name(name, db):
    """
    Найти билеты по имени исполнителя (в том числе – по подстроке),
    и выведите их по возрастанию цены
    """
    regex = re.compile(r'\w*{}\w*'.format(name))
    sorted_tickets = list(db.tickets_list.find({'Исполнитель': regex}).sort('Цена', pymongo.ASCENDING))
    for ticket in sorted_tickets:
        print('{} {} {}'.format(ticket['Дата'], ticket['Исполнитель'], ticket['Цена']))


def find_by_date(init_date, final_date, db):
    init_date = datetime.strptime(init_date, '%Y-%m-%d').date()
    final_date = datetime.strptime(final_date, '%Y-%m-%d').date()
    sorted_tickets = list(db.tickets_list.find({'Дата': {'$gte': init_date, '$lte': final_date}})
                          .sort('Дата', pymongo.ASCENDING))
    for ticket in sorted_tickets:
        print('{} {}'.format(ticket['Дата'], ticket['Исполнитель']))


if __name__ == '__main__':
    # read_data('artists.csv', tickets_db)
    # find_cheapest(tickets_db)
    # find_by_name('T', tickets_db)
    find_by_date('2019-07-01', '2019-07-30', tickets_db)

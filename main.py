import requests
from bs4 import BeautifulSoup
import re
import mysql.connector
import datetime

db = mysql.connector.connect(  # Connect to MySQL
    host='',  # Enter host
    user='',  # Enter username
    passwd='',  # Enter password to MySQL
    database=''  # Enter database
)

mycursor = db.cursor()


def create_tables(titles, len_titles):  # СCreate tables in MySQL
    for i in range(len_titles):
        exchange = titles[i].split(' ')[0] + '_goverla'
        mycursor.execute(
            'CREATE TABLE %s(id INT AUTO_INCREMENT PRIMARY KEY, bid FLOAT NOT NULL, ask FLOAT NOT NULL,dt DATETIME  NOT NULL)' % exchange)


def drop_all_tables(titles, len_titles):  # Drop tables in MySQL
    for i in range(len_titles):
        sql = 'DROP TABLE %s' % titles[i].split(' ')[0]
        mycursor.execute(sql)


def show_all_tables(titles, len_titles):  # Show all data  in MySQL
    for i in range(len_titles):
        exchange = titles[i].split(' ')[0] + '_goverla'
        mycursor.execute('SELECT * FROM %s' % exchange)
        myresult = mycursor.fetchall()
        print(titles[i].split(' ')[0])
        for x in myresult:
            print(x)


def write_data_to_sql_goverla(soup, titles, len_titles):  # Write data to MySQL
    print('\n')
    num = 0
    for bid, ask in zip(soup.find_all(class_="gvrl-table-cell bid"), soup.find_all(class_="gvrl-table-cell ask")):
        if num == len_titles:
            continue

        bid = str(bid)
        ask = str(ask)

        bid = re.findall(r'[0-9]', bid)
        if bid != []:
            bid = int(''.join(bid)) / 100

        ask = re.findall(r'[0-9]', ask)
        if ask != []:
            ask = int(''.join(ask)) / 100

        exchange = titles[num].split(' ')[0] + '_goverla'
        mycursor.execute(
            'INSERT INTO %s(bid, ask, dt) VALUES (%s, %s, NOW())' % (exchange, bid, ask))
        db.commit()
        num += 1


def write_exchange_rate_to_txt_goverla(titles, len_titles):  # Write exchangerate to .txt

    purchase = []
    selling = []

    difference_bid, difference_ask = analytics_with_yesterday_goverla(titles, len_titles)

    for i in range(len_titles):  # bid
        exchange_goverla = titles[i].split(' ')[0] + '_goverla'
        mycursor.execute('SELECT (bid) FROM %s' % exchange_goverla)
        myresult = mycursor.fetchall()
        purchase.append(myresult[-1])

    for i in range(len_titles):  # ask
        exchange_goverla = titles[i].split(' ')[0] + '_goverla'
        mycursor.execute('SELECT (ask) FROM %s' % exchange_goverla)
        myresult = mycursor.fetchall()
        selling.append(myresult[-1])

    date_today = datetime.datetime.today().strftime(
        "%d:%m:%Y")  # Запис курса валюти в .txt
    file = 'exchangerate' + date_today + '.txt'
    with open(file, 'w+') as f:
        f.write('Курс на ' + datetime.datetime.today().strftime("%d/%m/%Y"))
        f.write('\n')
        for i, j in zip(range(len_titles), range(len_titles)):
            bid = float(list(purchase[i])[0])
            ask = float(list(selling[i])[0])
            f.write(titles[i])
            f.write('\n')
            f.write('Купівля: ' + str(bid) + '(' + str(difference_bid[i]) + ')')
            f.write('\n')
            f.write('Продаж: ' + str(ask) + '(' + str(difference_ask[i]) + ')')
            f.write('\n')


def analytics_with_yesterday_goverla(titles, len_titles):  # Price comparison with yesterday
    difference = []
    for i in range(len_titles):
        exchange_goverla = titles[i].split(' ')[0] + '_goverla'
        mycursor.execute('SELECT bid, ask FROM %s' % exchange_goverla)
        myresult = mycursor.fetchall()
        myresult_today = myresult[-1]
        myresult_yesterday = myresult[-2]
        for today, yesterday in zip(myresult_today, myresult_yesterday):
            difference.append(round(float(today - yesterday), 2))
    return difference[::2], difference[1::2]


def parsing_goverla():
    BASE_URL = 'https://goverla.ua'  # Site
    page = requests.get(BASE_URL)  # Requests to site
    soup = BeautifulSoup(page.text, 'html.parser')
    titles = [div['title'] for div in soup.find_all('img', title=True)]
    len_titles = len(titles)
    write_data_to_sql_goverla(soup, titles, len_titles)
    write_exchange_rate_to_txt_goverla(titles, len_titles)


def main():
    print('Start parsing goverla')
    parsing_goverla()
    print('Finish parsing goverla')


if __name__ == '__main__':
    main()

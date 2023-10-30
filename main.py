import requests
import selectorlib
import os
import smtplib,ssl
import time
import sqlite3


URL = 'http://programmer100.pythonanywhere.com/tours/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

connection = sqlite3.connect('data.db')

def scrape(url):
    ''' Scrape the page source from the URL'''
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def send_email(message):
    host = 'smtp.gmail.com'
    port = 465

    # Senders email address
    username = 'rajanchakravarthy@gmail.com'
    password = os.getenv('PASSWORD')

    # Receivers email address
    receiver = 'rajanchakravarthy@gmail.com'

    my_context = ssl.create_default_context()


    with smtplib.SMTP_SSL(host, port, context=my_context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)


def read(extracted):
    row = extracted.split(',')
    band, city, date = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM events WHERE band=? AND city=? AND date=?',(band, city, date))
    rows = cursor.fetchall()
    print(rows)
    return rows


def store(extracted):
    row = extracted.split(',')
    new_row = [item.strip() for item in row]
    cursor = connection.cursor()
    cursor.execute('INSERT INTO events VALUES(?,?,?)', new_row)
    connection.commit()


def extract(source):
    ''' Extracts required information from a source page
        key used here is tours --> corresponds to id: displaytimer in extract.yaml '''

    extractor = selectorlib.Extractor.from_yaml_file('extract.yaml')
    value = extractor.extract(source)['tours']
    return value


if __name__ == '__main__':
    while True:
        # information from the url in obtained
        scraped = scrape(URL)
        # extracts the required information based on the key filter
        extracted = extract(scraped)
        print(extracted)
        ''' 
        # checks if path data.txt exists
        if not os.path.exists('data.txt'):
            with open('data.txt', mode='w'):
                pass
        '''


        if extracted.lower() != 'no upcoming tours':
            rows = read(extracted)
            if not rows:
                store(extracted)
                email_message = '''Subject: NEW EVENT!!!\n
                
                Topic: New event was found.
                '''
                send_email(message=email_message)

        time.sleep(1)
import re
from urllib.error import HTTPError
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pymongo import MongoClient


def connectDataBase():
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")


def create_html(col, url, html):
    document = {
        'url': url,
        'html': html
    }
    col.insert_one(document)


def find_page(page, target):
    db = connectDataBase()
    page_db = db['pages']

    frontier = []
    visited_links = set()
    starting_website = page
    frontier.append(starting_website)
    target_url = ''

    while frontier:
        current_page = frontier.pop(0)
        print("Crawling ", current_page)

        if current_page in visited_links:
            continue

        visited_links.add(current_page)

        try:
            html = urlopen(current_page)
            html_content = html.read()
            bs = BeautifulSoup(html_content, "html.parser")
            create_html(page_db, current_page, str(bs))
        except HTTPError as e:
            continue

        if bs.h1 is not None and bs.h1.text == target:
            target_url = current_page
            frontier = []
        else:
            for link in bs.find_all(name="a"):
                if re.match('^/.*s?(html)$', link.get('href')):
                    frontier.append('https://www.cpp.edu' + link.get('href'))
                elif re.match('^(https).*s?(html)$', link.get('href')):
                    frontier.append(link.get('href'))

    print("all site crawled!")
    print('Target page: ', target_url)
    return target_url


if __name__ == '__main__':
    url = 'https://www.cpp.edu/sci/computer-science/'
    find_page(url, 'Permanent Faculty')

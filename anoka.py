import scrapy
from scrapy.crawler import CrawlerProcess
import requests
from lxml import html
from lxml import etree
import itertools
import math
import json
from sqlalchemy import *
import math
from locations import get_location
import re
import datetime
import urllib
from isbn_converter import isbn13_to_isbn10


class LibrarySpider(scrapy.Spider):
    name = 'library'

    db_connection = "mysql+pymysql://library:pass@localhost/library"
    engine = create_engine(db_connection, echo=True)
    conn = engine.connect()
    meta = MetaData()
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }
    books = Table('books', meta,
                  Column('id', Integer, primary_key=True, autoincrement=True),
                  Column('title', String(50)),
                  Column('cover', String(60)),
                  Column('author', String(60)),
                  Column('author_2', String(60)),
                  Column('author_3', String(60)),
                  Column('author_4', String(60)),
                  Column('author_5', String(60)),
                  Column('description', String(600000)),
                  Column('collection', String(60)),
                  Column('link', String(60)),
                  Column('isbn', String(60)),
                  Column('county', String(60)),
                  Column('county_2', String(60)),
                  Column('location', String(60)),
                  Column('rating', Float),
                  Column('page_num', Integer),
                  Column('publisher', String(60)),
                  Column('category', String(60)),
                  Column('category_2', String(60)),
                  Column('category_3', String(60)),
                  Column('category_4', String(60)),
                  Column('category_5', String(60)),
                  Column('published_date', Date),
                  Column('greater_minnesota', Boolean),
                  Column('num_ratings', Integer)
                  )

    meta.create_all(engine)

    def start_requests(self):
        page = requests.get(
            "https://anok.ent.sirsi.net/client/en_US/default/search/results?qf=LANGUAGE%09Language%09ENG%09English&qf=ITEMCAT2%09Audience%091%3AADULT%09Adult&qf=FORMAT%09Format%09BOOK%09Books&isd=true&av=0")
        page_tree = html.fromstring(page.content)

        books = page_tree.xpath(
            '//*[@id="searchResultsColumn"]/div[1]/div/div[2]/div[1]')[0].text
        num_books = re.sub("\D", "", books)

        for i in range(1, math.ceil(int(num_books)/12) + 1):
            yield scrapy.Request(url=f"https://anok.ent.sirsi.net/client/en_US/default/search/results?qf=LANGUAGE%09Language%09ENG%09English&qf=ITEMCAT2%09Audience%091%3AADULT%09Adult&qf=FORMAT%09Format%09BOOK%09Books&rw={12*(i-1)}&isd=true&av=0", callback=self.check_available, cb_kwargs=dict(starting_index=12*(i-1)))

    def check_available(self, response, starting_index):
        for i in range(starting_index, starting_index+12):
            if(response.xpath(f'//*[@id="detailLink{i}"]').xpath('@href').get() == None):
                print("The selector is " + f'//*[@id="detailLink{i}"]')
                print("The value is " + str(response.xpath(f'//*[@id="detailLink{i}"]')))
                file = open(f"html_{starting_index}.html", "w")
                file.write(str(response.body))
            print("The link is "+str(response.xpath(f'//*[@id="detailLink{i}"]').xpath('@href').get()))
            book_link = "https://anok.ent.sirsi.net/" + str(response.xpath(f'//*[@id="detailLink{i}"]').xpath('@href').get())
            yield scrapy.Request(url=book_link, cb_kwargs=dict(collection=''))

    def parse(self, response, collection):

        num_rating = 0
        book_rating = 0
        cat_len = 0
        author_len = 0
        asin = ''
        Description = ''

        isbn = response.xpath(
            '//*[@id="detail_biblio0"]/div[3]/div/div/div[2]').xpath("text()").get()

        if((isbn is None) or isbn[0].isdigit() == False):
            asin = '4444444444'
        else:
            asin = isbn13_to_isbn10(isbn)

        if(response.xpath('//*[@id="detail_biblio0"]/div[9]/div/div/div[2]').xpath("text()").get() is None):
            Description = ''

        else:
            Description = response.xpath(
                '//*[@id="detail_biblio0"]/div[9]/div/div/div[2]').xpath("text()").get().strip()

        t = text(f"select avg(overall) - 1/sqrt(count(*)) as actualRating, count(*) from amazon_comments where asin='{asin}'")
        title = response.xpath(
            '//*[@id="detail_biblio0"]/div[1]/div/div/div[2]').xpath("text()").get().strip()

        volumeInfo = []

        bookHeadings = ['publisher', 'authors',
                        "categories", 'pageCount', 'publishedDate']
        bookInfo = []

        publisher = []
        author = []
        author += []
        categories = []
        page_count = []

        categories += [''] * (5-cat_len)
        book_rating = None
        book_num = 0

        ratings = self.conn.execute(t).first().values()
        book_rating = ratings[0]
        book_num = ratings[1]

        ins = self.books.insert().values(cover=response.css("#detailCover0").xpath("@src").get(), title=title,
                                         author=[''], author_2=[''], author_3=[''], author_4=[''], author_5=[''], category=[''], category_2=[''], category_3=[''], category_4=[''], category_5=[''], description=Description,
                                         collection=collection, isbn=isbn, link=response.request.url, page_num=0, county="Anoka", greater_minnesota=False, rating=book_rating,  num_ratings=book_num, publisher=[''])

        conn = self.engine.connect()
        result = conn.execute(ins)

        return{

        }


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(LibrarySpider)
process.start()

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


class LibrarySpider(scrapy.Spider):
    name = 'library'

    db_connection = "mysql+pymysql://library:pass@localhost/library"
    engine = create_engine(db_connection, echo=True)
    meta = MetaData()

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
            "https://hclib.bibliocommons.com/v2/search?custom_edit=false&query=isolanguage%3A%22eng%22%20formatcode%3A(BK%20OR%20AB%20)&searchType=bl&f_FORMAT=BK&f_CIRC=CIRC&f_STATUS=_anywhere_&f_AUDIENCE=adult")
        page_tree = html.fromstring(page.content)

        books = page_tree.xpath(
            "/html/body/div/div/div/div[5]/div/div/div/div[2]/div[2]/section/section[1]/div[2]/span")[0].text
        num_books = books[11:18].replace(",", "")

        for i in range(1, 101):
            yield scrapy.Request(url=f"https://hclib.bibliocommons.com/v2/search?custom_edit=false&query=isolanguage%3A%22eng%22%20formatcode%3A(BK%20OR%20AB%20)&searchType=bl&f_FORMAT=BK&f_CIRC=CIRC&f_STATUS=_anywhere_&f_AUDIENCE=adult&pagination_page={i}", callback=self.check_available)

    def check_available(self, response):
        for book in response.css("[data-key='search-result-item']"):
            book_link = book.css("[data-key='bib-title']::attr(href)").get()
            book_type = book.css(".cp-call-number").xpath("text()").get()
            yield scrapy.Request(url="https://hclib.bibliocommons.com"+str(book_link), cb_kwargs=dict(collection=book_type))

    def parse(self, response, collection):

        num_rating = 0
        book_rating = 0
        cat_len = 0
        author_len = 0

        isbn = response.css(".jacketCover").xpath("@src").get()[45:58]
        title = response.css(".item_bib_title").xpath("text()").get().strip()

        print("The isbn is "+isbn)
        book = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=+isbn:{isbn}")
        bookInfo = book.json()

        try:
            volumeInfo = bookInfo["items"][0]["volumeInfo"]
        except KeyError:
            print("isbn not found, resorting to title")
            url = "https://www.googleapis.com/books/v1/volumes?q=" + \
                urllib.parse.quote(title)
            bookInfo = requests.get(url).json()
            print("The url is "+f"https://www.googleapis.com/books/v1/volumes?q={title}")
            try:
                volumeInfo = bookInfo["items"][0]["volumeInfo"]
            except KeyError:
                print("The volume here is "+ str(bookInfo))
                volumeInfo = bookInfo["items"][0]["volumeInfo"]       
                print("The title is "+title)

        bookHeadings = ['publisher', 'authors',
                        "categories", 'pageCount', 'publishedDate']
        bookInfo = [volumeInfo.get(heading, ['']) for heading in bookHeadings]
        print("The book information is " + str(bookInfo))

        publisher = bookInfo[0]
        author = bookInfo[1]
        author += [''] * (5-author_len)
        categories = bookInfo[2]
        page_count = bookInfo[3]

        categories += [''] * (5-cat_len)

        try:
            book_num = volumeInfo['ratingsCount']
            book_rating = volumeInfo['averageRating']
            book_rating = book_rating - 1/math.sqrt(book_num)
        except KeyError:
            book_rating = None
            book_num = 0

        ins = self.books.insert().values(cover=response.css(".jacketCover").xpath("@src").get(), title=response.css(".item_bib_title").xpath("text()").get().strip(),
                                         author=author[0], author_2=author[1], author_3=author[2], author_4=author[3], author_5=author[4], category=categories[0], category_2=categories[1], category_3=categories[2], category_4=categories[3], category_5=categories[4], description=response.css(
            ".bib_description").xpath("text()").get().strip(),
            collection=collection, isbn=isbn, link=response.request.url, page_num=page_count, county="Hennepin", greater_minnesota=False, rating=book_rating,  num_ratings=book_num, publisher=publisher, page_num=page_count)

        conn = self.engine.connect()
        result = conn.execute(ins)

        return{
            "Cover": response.css(".jacketCover").xpath("@src").get(),
            "Title": response.css(".item_bib_title").xpath("text()").get().strip(),
            "Description": response.css(".bib_description").xpath("text()").get().strip(),
            "Collection": collection,
            "Link": response.request.url,
            "ISBN": response.css(".jacketCover").xpath("@src").get()[45:58]
        }


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(LibrarySpider)
process.start()

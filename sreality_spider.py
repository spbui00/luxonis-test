import scrapy
import json
import psycopg2
from psycopg2 import sql, extensions
from scrapy.crawler import CrawlerProcess
import os

class SRealitySpider(scrapy.Spider):
    name = "sreality"
    start_urls = [
        "https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&per_page=500",
    ]

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['_embedded']['estates']:
            yield {
                'title': item['name'],
                'image_urls': [link['href'] for link in item['_links']['images']]
            }

class PostgreSQLPipeline(object):
    def open_spider(self, spider):
        hostname='db'
        username='postgres'
        password=os.getenv('POSTGRES_PASSWORD')
        database='sreality'

        # Connect to the default "postgres" database
        conn = psycopg2.connect(host=hostname, user=username, password=password, dbname='postgres')
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT) 

        # Create a new cursor
        cur = conn.cursor()

        # Check if the database exists
        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), (database,))
        if cur.fetchone() is None:
            # If the database does not exist, create it
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database)))
        
        cur.close()
        conn.close()

        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id SERIAL PRIMARY KEY,
                title TEXT,
                image_urls TEXT[]
            )
        """)
    
    def close_spider(self, spider):
        self.cur.close()
        self.connection.close()

    def process_item(self, item, spider):
        self.cur.execute("insert into ads(title, image_urls) values(%s,%s)", 
                        (item['title'], item['image_urls']))
        self.connection.commit()
        return item

process = CrawlerProcess({
    'ITEM_PIPELINES': {__name__ + '.PostgreSQLPipeline': 1},
})

process.crawl(SRealitySpider)
process.start()
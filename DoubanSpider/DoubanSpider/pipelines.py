# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import datetime
from pymongo import MongoClient
from scrapy import log

class Statics:
    movie_parsed=0;
    start_time=datetime.datetime.now()

class DoubanspiderPipeline(object):
    is_db_connected=False
    douban_db=None
    movie_collection=None
    spider_statics=Statics()
    
    def __init__(self):
        client=MongoClient('localhost',27017)
        self.douban_db = client.douban_db
        self.movie_collection=self.douban_db.movie_collection
        self.is_db_connected=True

    def process_item(self, item, spider):
        self.spider_statics.movie_parsed+=1
        log.msg(("Parsed Movies: {}").format(self.spider_statics.movie_parsed),level=log.INFO)
        log.msg(("Running Time: {}\n").format(datetime.datetime.now()-self.spider_statics.start_time),level=log.INFO)

        # process item
        self.movie_collection.insert(dict(item))
        return item

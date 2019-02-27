# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanspiderItem(scrapy.Item):
    id=scrapy.Field()
    title=scrapy.Field()
    directors=scrapy.Field()
    rate=scrapy.Field()
    star=scrapy.Field()
    casts=scrapy.Field()
    genres=scrapy.Field()
    imdb_id=scrapy.Field()
    summary=scrapy.Field()
    comments=scrapy.Field()
    cover=scrapy.Field()

import scrapy
import json
import requests
from DoubanSpider.items import DoubanspiderItem

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

class DoubanSpider(scrapy.Spider):
    name="douban"
    allowed_domains=["douban.com"]
    start_urls=[
        "https://movie.douban.com/j/new_search_subjects?sort=T&range=0,100&tags=%E7%94%B5%E5%BD%B1&start=0"
    ]
    flag=True
    movie_start_count=20
    comment_start_count=0
    # parse from json send back by douban.com
    def parse(self,response):
        if response.status != 200:
            log.msg("Response Error",level=log.INFO)
            yield scrapy.Request(response.url,callback=self.parse)
        else:
            response_json=json.loads(response.body)
            for movie_item in response_json['data']:
                item=DoubanspiderItem()
                item['directors']=movie_item['directors']
                item['rate']=movie_item['rate']
                item['title']=movie_item['title']
                item['casts']=movie_item['casts']
                item['star']=movie_item['star']
                item['id']=movie_item['id']
                item['cover']=movie_item['cover']
                yield scrapy.Request(movie_item['url'],callback=self.parseMovieDetail,meta={'item':item})
            
            for self.movie_start_count in range(self.movie_start_count,40,20):
                yield scrapy.Request(("https://movie.douban.com/j/new_search_subjects?sort=T&range=0,100&tags=%E7%94%B5%E5%BD%B1&start={}").format(self.movie_start_count),callback=self.parse)

    # parse movie detail in movie object page
    def parseMovieDetail(self,response):
        if response.status != 200:
            log.msg("Response Error",level=log.INFO)
            yield scrapy.Request(response.url,callback=self.parseMovieDetail)
        else:
            item = response.meta['item']
            item['genres']=[]
            for span in response.xpath('//span[@property="v:genre"]'):
                item['genres'].append(span.xpath('text()').extract())

            item['summary']=response.xpath('//*[@id="link-report"]/span[1]/text()').extract()
            item['imdb_id']=response.xpath('//*[@id="info"]/a/text()').extract()

            # read 100 comments
            for self.comment_start_count in range(self.comment_start_count,100,20):
                yield scrapy.Request(("https://movie.douban.com/subject/{}/comments?start={}&limit=20&sort=new_score&status=P").format(item['id'],self.comment_start_count),callback=self.parseMovieComments,meta={'item':item})

    # parse comments in comment pages
    def parseMovieComments(self,response):
            item = response.meta['item']
            item['comments']=[]
            for comment in response.xpath('//div[@class="comment-item"]'):
                comment_detail = {}
                comment_detail['commentor']=comment.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/a/text()').extract()
                comment_detail['commentor_rate']=comment.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[@class="allstar40 rating"]/@title').extract()
                comment_detail['content']=comment.xpath('div[@class="comment"]/p/span/text()').extract()
                item['comments'].append(comment_detail)
            return item


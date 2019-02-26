import scrapy
from DoubanSpider.items import DoubanspiderItem

class DoubanSpider(scrapy.Spider):
    name="douban"
    allowed_domains=["douban.com"]
    start_urls=[
        "https://movie.douban.com/subject/26266893/"
    ]

    def parse(self,response):
        item=DoubanspiderItem()
        item['title']=response.xpath('/div[@id="content"]/h1/span[@property=v:itemreviewed]/text()').extract()
        print('title ')
        print(item['title'])
        hot_comment_list=response.xpath('//div[@class="comment-item"]')
        for i in range(1,len(hot_comment_list)+1):
            user_name=response.xpath('/div[@class="comment-item"][{}]/a/text()'.format(i)).extract()
            user_rating=dist()
            user_rating['rating']=response.xpath('/div[@class="comment-item"][{}]/span[@class="allstar10 rating"]/@title'.format(i)).extract()
            user_rating['comment']=response.xpath('/div[@class="comment-item"][{}]/span[@class="hide-item full"]/text()'.format(i)).extract()
            item['comments'][user_name]=user_rating

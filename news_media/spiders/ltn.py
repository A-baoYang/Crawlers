import scrapy
from news_media.items import NewsMediaItem


class LtnSpider(scrapy.Spider):
    name = "ltn"
    allowed_domains = ["search.ltn.com.tw"]
    start_urls = [
        "https://search.ltn.com.tw/list?keyword=%E5%8D%8A%E5%B0%8E%E9%AB%94&type=all&sort=date"
    ]

    def parse(self, response):
        item = NewsMediaItem()
        item["title"] = response.xpath('//a[@class="tit"]/text()').getall()
        item["url"] = response.xpath('//a[@class="http"]/@href').getall()
        item["desc"] = response.xpath('//div[@class="cont"]/p/text()').getall()
        yield item

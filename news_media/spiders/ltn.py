import scrapy


class LtnSpider(scrapy.Spider):
    name = 'ltn'
    allowed_domains = ['search.ltn.com.tw']
    start_urls = [f'http://search.ltn.com.tw/list?keyword={keyword}&type=all&sort=date&start_time={start_time}&end_time={end_time}&page={i}']

    def parse(self, response):
        pass

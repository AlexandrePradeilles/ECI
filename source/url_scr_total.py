import scrapy
from scrapy.crawler import CrawlerProcess

class Spider20Minutes(scrapy.Spider):
    name = '20minutes'
    start_urls = ['https://www.20minutes.fr/archives/20' + str(i) for i in range(10, 23)] + ['https://www.20minutes.fr/archives/200' + str(i) for i in range(6, 10)]

    custom_settings = {
        'FEED_URI': 'data/newspaper_url.jsonl',
        'FEED_FORMAT': 'jsonl',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    def parse(self, response):
        links = response.xpath('//div[@class="box brick mb2 month"]//@href').getall()
        for link in links:
            yield response.follow(link, callback = self.parse_day)

    def parse_day(self, response):
        links = response.xpath('//ul[@class="spreadlist"]//@href').getall()
        for link in links:
            yield {
            'article_url': link
            }


if __name__=='__main__':
    process = CrawlerProcess()
    process.crawl(Spider20Minutes)
    process.start()
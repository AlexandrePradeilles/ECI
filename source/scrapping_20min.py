import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess


user_agent_list = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363',
]

class Spider20Minutes(scrapy.Spider):
    name = '20minutes'
    df = pd.read_parquet("./data/urls.parquet")
    start_urls = list(df.url.values)
    # start_urls = ['https://www.20minutes.fr/archives/20' + str(i) for i in range(10, 23)] #+ ['https://www.20minutes.fr/archives/200' + str(i) for i in range(6, 10)]
    
    custom_settings = {
        'FEED_URI': './data/newspaper_part4.jsonl',
        'FEED_FORMAT': 'jsonl',
        'FEED_EXPORT_ENCODING': 'utf-8'
    }

    # def parse(self, response):
    #     links = response.xpath('//div[@class="box brick mb2 month"]//@href').getall()
    #     for link in links:
    #         yield response.follow(link, callback = self.parse_day)

    # def parse_day(self, response):
    #     links = response.xpath('//ul[@class="spreadlist"]//@href').getall()
    #     for link in links:
    #         yield response.follow(link, callback = self.parse_link, cb_kwargs={'url': 'https://www.20minutes.fr' + link})

    def parse(self, response):
        link = response.request.url
        title = response.xpath('//article[@id="main-content"]//h1[@class="nodeheader-title"]/text()').get()
        summary = response.xpath('//article[@id="main-content"]//span[@class="hat-summary"]/text()').get()
        article_date = response.xpath('//article[@id="main-content"]//div[@class="datetime"]//@datetime').get()
        body_html = response.xpath('//article[@id="main-content"]//div[@class="lt-endor-body content"]//div[@class="qiota_reserve content"]/p//text() | //article[@id="main-content"]//div[@class="lt-endor-body content"]//div[@class="qiota_reserve content"]/h2//text() | //article[@id="main-content"]//div[@class="lt-endor-body content mt1"]//p//text()').getall()

        body = " ".join(body_html).replace("\xa0", " ")
        
        image_url = response.xpath('//article[@id="main-content"]//div[@class="lt-endor-body content"]//div[@class="media-wrap"]//@src').get()
        
        try:
            category = link.split('.fr/')[1].split('/')[0]

        except:
            category= "undefined"
        date = pd.to_datetime('today')


        yield {
            'article_url': link,
            'title': title,
            'summary': summary,
            'article_date': article_date,
            'body': body,
            'image_url': image_url,
            'category_id': category,
            'journal_id': 1,
            'scraping_date': str(date)
        }


if __name__=='__main__':
    process = CrawlerProcess()
    process.crawl(Spider20Minutes)
    process.start()
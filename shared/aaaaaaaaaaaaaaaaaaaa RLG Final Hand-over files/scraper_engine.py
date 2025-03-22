import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import logging
import os

class RLGDataScraper(scrapy.Spider):
    name = "rlg_data_scraper"
    allowed_domains = ["example.com"]  # Update with actual domains
    start_urls = ["https://example.com"]  # Update with actual URLs

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output_data.json',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'ROBOTSTXT_OBEY': True,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
    }

    def parse(self, response):
        for item in response.css('div.item'):  # Adjust selector based on website structure
            yield {
                'title': item.css('h2::text').get(),
                'price': item.css('span.price::text').get(),
                'url': response.urljoin(item.css('a::attr(href)').get()),
            }

if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(RLGDataScraper)
    process.start()

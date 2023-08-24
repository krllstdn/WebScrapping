from scrapy import Spider, Request
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib.parse import urljoin
import logging
import time


class SRealitySpider(Spider):
    name = 'sreality'
    start_urls = ['https://www.sreality.cz/hledani/pronajem/byty/praha']
    item_count = 0
    page_count = 2

    def __init__(self):
        super().__init__()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        caps = DesiredCapabilities.CHROME
        for key, value in caps.items():
            chrome_options.set_capability(key, value)
        
        self.driver = webdriver.Remote(
            command_executor='http://172.20.0.2:4444/wd/hub',
            options=chrome_options
        )

    def start_requests(self):
        for url in self.start_urls:
            logging.info(f"Starting scraping for URL: {url}")
            yield Request(url, callback=self.parse, meta={'use_selenium': True})

    def parse(self, response):
        # Check if Selenium was used for this request
        if response.meta.get('use_selenium'):
            self.driver.get(response.url)

            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            for _ in range(5):  
                self.driver.execute_script("window.scrollBy(0, 800);") 
                time.sleep(2)

            body = self.driver.page_source
            # Create a new response with the content from Selenium
            response = response.replace(body=body)
        

        # Continue with your parsing logic
        for flat in response.xpath('//div[contains(@class, "property")]'):
            item = {
                'title': flat.xpath('.//h2/a/span[@class="name ng-binding"]/text()').get(),
                'image_url': flat.xpath('.//img/@src').get()
            }

            self.item_count += 1
            logging.info(f"{self.item_count}. Scraped item: {item['title']}")

            yield item

            if self.item_count == 500:
                logging.info("Reached the goal of 500 items. Closing spider.")
                self.driver.quit()
                return

        if self.item_count < 500:
            next_page = response.xpath('//a[contains(@class, "paging-next")]/@href').get()
            pag_url = 'https://www.sreality.cz/hledani/pronajem/byty/praha?strana='

            if next_page:
                next_page = urljoin(response.url, next_page)
                logging.info(f"Navigating to next page: {next_page}")
                yield Request(next_page, callback=self.parse, meta={'use_selenium': True})
            else:
                logging.warning("Next page not found. The spider might stop before reaching 500 items.")
                # logging.info(response.text)

    # def closed(self, reason):
    #     logging.info("Spider closed. Closing the Selenium driver.")
    #     self.driver.quit()


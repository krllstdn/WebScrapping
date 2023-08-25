import logging
import time
from urllib.parse import urljoin

from scrapy import Request, Spider
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from sreality.items import SrealityItem


class SRealitySpider(Spider):
    name = "sreality"
    start_urls = ["https://www.sreality.cz/hledani/pronajem/byty/praha"]
    item_count = 0
    page_count = 2
    NUMBER_TO_SCRAPE = 500

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
            command_executor="http://selenium:4444/wd/hub", options=chrome_options
        )

    def start_requests(self):
        for url in self.start_urls:
            logging.info(f"Starting scraping for URL: {url}")
            yield Request(url, callback=self.parse, meta={"use_selenium": True})

    def parse(self, response):
        if response.meta.get("use_selenium"):
            self.driver.get(response.url)

            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(2)

            body = self.driver.page_source
            response = response.replace(body=body)

        for flat in response.xpath(
            '//div[@class="dir-property-list"]/div[contains(@class, "property")]'
        ):
            item = SrealityItem()
            item["title"] = flat.xpath(
                './/h2/a/span[@class="name ng-binding"]/text()'
            ).get()
            item["image_url"] = flat.xpath(".//img/@src").get()

            self.item_count += 1

            yield item

            if self.item_count == self.NUMBER_TO_SCRAPE:
                logging.info(
                    f"Reached the goal of {self.NUMBER_TO_SCRAPE} items. Closing spider."
                )
                self.driver.quit()
                return

        if self.item_count < self.NUMBER_TO_SCRAPE:
            next_page = response.xpath(
                '//a[contains(@class, "paging-next")]/@href'
            ).get()

            if next_page:
                next_page = urljoin(response.url, next_page)
                logging.info(f"Navigating to next page: {next_page}")
                yield Request(
                    next_page, callback=self.parse, meta={"use_selenium": True}
                )
            else:
                logging.warning(
                    "Next page not found. The spider might stop before reaching 500 items."
                )

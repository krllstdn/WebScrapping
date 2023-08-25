BOT_NAME = 'sreality'
SPIDER_MODULES = ['sreality.spiders']
NEWSPIDER_MODULE = 'sreality.spiders'

SELENIUM_DRIVER_NAME = 'remote'
SELENIUM_COMMAND_EXECUTOR = 'http://selenium:4444/wd/hub'
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}
DOWNLOAD_DELAY = 3  # Adjust as necessary
CONCURRENT_REQUESTS = 1  # Adjust based on your system's capabilities
LOG_LEVEL = 'INFO'

DATABASE_URL = "postgresql://user:password@db:5432/mydatabase"

ITEM_PIPELINES = {
    'sreality.pipelines.DatabasePipeline': 1,
}

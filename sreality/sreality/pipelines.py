# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, inspect
from sqlalchemy.orm import sessionmaker

class SrealityPipeline:
    def process_item(self, item, spider):
        return item


class DatabasePipeline:
    def __init__(self, database_url):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            database_url=crawler.settings.get('DATABASE_URL')
        )

    def open_spider(self, spider):
        self.engine = create_engine(self.database_url, pool_size=10, max_overflow=20)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Define your table schema here
        self.items_table = Table('items', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('title', String),
            Column('image_url', String)
        )

        inspector = inspect(self.engine)
        
        if "items" in inspector.get_table_names():
            self.items_table.drop(self.engine)

        self.metadata.create_all(self.engine)

    def close_spider(self, spider):
        self.session.close()
        self.engine.dispose()

    def process_item(self, item, spider):
        ins = self.items_table.insert().values(
            title=item['title'],
            image_url=item['image_url']
        )
        try:
            self.session.execute(ins)
            self.session.commit()
        except Exception as e:
            spider.logger.error(f"Error inserting item: {item['title']}. Error: {e}")
            self.session.rollback()
            
        return item

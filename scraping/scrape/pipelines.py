# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class TutorialPipeline:
    def process_item(self, item, spider):
        return item



class IDpipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("title"):
            return item
        else:
            print("------------------------------DROPPED----------------")
            raise DropItem(f"Missing title in {item}")
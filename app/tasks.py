from scrapy.crawler import CrawlerRunner

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scraper.PSNScraper import PSNScraper, GeneralScraper

from crochet import run_in_reactor, setup

# from scrapy.signalmanager import dispatcher
from scrapy import signals
    
import time



setup()

@run_in_reactor    
def run_scrape(country_name={'country': "Thailand"}):
    print("----------------Scraping Started---------------------")
    configure_logging()
    process_scrape_settings(country_name)
    settings = get_project_settings()
    settings['FEEDS'] = {'psngames.json': {'format': 'json', 'overwrite': 'true'}}
    settings['ITEM_PIPELINES'] = {
        "scraper.pipelines.IDpipeline": 300
    }

    runner = CrawlerRunner(settings=settings)
    # dispatcher.connect(spider_closed_action, signals.spider_closed)
    runner.crawl(PSNScraper)

@run_in_reactor
def scrape_countries():
    print("----------------Scraping countries Started---------------------")
    configure_logging()
    settings = get_project_settings()
    settings['FEEDS'] = {'countries.json': {'format': 'json', 'overwrite': 'true'}}
    data = {          'start_url': 'https://store.playstation.com/en-gb/pages/browse',
                     'item_links' : False,
                     'item_css': '.psw-link.psw-content-link.psw-l-anchor.psw-interactive-root',
                     'multiple_pages': False,
                     'next_page_url': '',
                     'next_page_url_add': '',
                     'attributes_dict': {
                                         'link': '.psw-link.psw-content-link.psw-l-anchor.psw-interactive-root::attr(href)'
                                         }
                     }
    runner = CrawlerRunner(settings=settings)
    runner.crawl(GeneralScraper, scrape_settings=data)


def check_scrape_status():
    print("----------------Checking Scraping Status---------------------")
    
    return True

def process_scrape_settings(country_name):
    json = {'country' : country_name}
    return json

  



from scrapy.crawler import CrawlerRunner

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scraper.PSNScraper import PSNScraper, PSNCountryScraper
import json
import os
from crochet import run_in_reactor, setup

# from scrapy.signalmanager import dispatcher
from scrapy import signals
    
import time



setup()


def get_country_list():
    json_path = os.path.join(os.getcwd(), 'datafolder\\countries.json')
    with open(json_path, 'r') as json_file:
        data = sorted(json.load(json_file),key=lambda x:x["country"])    

    return data
    

@run_in_reactor    
def run_scrape(country_code):
    print("----------------Scraping Started---------------------")
    configure_logging()

    settings = get_project_settings()   

    settings['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    settings['FEEDS'] = {f'.\\datafolder\\psngames-{country_code}.json': {'format': 'json', 'overwrite': 'true'}}
    settings['ITEM_PIPELINES'] = {
        "scraper.pipelines.IDpipeline": 300
    }
    data = {
        'shortcode': country_code
    }
    
    runner = CrawlerRunner(settings=settings)
    # dispatcher.connect(spider_closed_action, signals.spider_closed)
    runner.crawl(PSNScraper, scrape_settings=data)


@run_in_reactor
def run_countries_scrape():
    print("----------------Scraping countries Started---------------------")
    configure_logging()
    settings = get_project_settings()
    settings['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    settings['FEEDS'] = {'.\\datafolder\\countries.json': {'format': 'json', 'overwrite': 'true'}}
    data = {          'start_url': 'https://store.playstation.com/en-gb/pages/browse',
                     'item_links' : False,
                     'item_css': '//script[contains(@id,"env")]',
                     'scrape_json': True,
                     'multiple_pages': False,
                     'next_page_url': '',
                     'next_page_url_add': '',
                     'attributes_dict': {
                                         'link': '.psw-link.psw-content-link.psw-l-anchor.psw-interactive-root::attr(href)'
                                         }
                     }
    runner = CrawlerRunner(settings=settings)
    runner.crawl(PSNCountryScraper, scrape_settings=data)


def check_scrape_status():
    print("----------------Checking Scraping Status---------------------")
    
    return True

def process_scrape_settings(country_name):
    json = {'shortcode' : country_name}
    return json

  



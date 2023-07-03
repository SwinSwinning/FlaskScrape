from scrapy.crawler import CrawlerRunner

from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scraper.PSNScraper import PSNScraper, PSNCountryScraper, GeneralScraper
import json
import os
from crochet import run_in_reactor, setup

# from scrapy.signalmanager import dispatcher
from scrapy import signals
    


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
def PSNscrape(country_shortcode):
    print("----------------Scraping Started---------------------")
    configure_logging()

    settings = get_project_settings()   

    settings['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    settings['FEEDS'] = {f'.\\datafolder\\psngames-{country_shortcode}.json': {'format': 'json', 'overwrite': 'true'}}
    settings['ITEM_PIPELINES'] = {
       "scraper.pipelines.IDpipeline": 300
    }
     
    scr_settings = {  'start_url': f'https://store.playstation.com/{country_shortcode}/pages/browse/1',
                'item_links': True,
                'item_css': '//a[@class="psw-link psw-content-link"]',
                'next_page_url': '//button[@data-qa="ems-sdk-grid#ems-sdk-top-paginator-root#next"]',
                'next_page_url_add': 'value',
                'multiple_pages': True,
                'scrape_json': False,
                'attributes':{
                                'title': ['h1.psw-m-b-5', ''],
                                'price': ['span[data-qa="mfeCtaMain#offer0#finalPrice"]',''],
                                'imglink': ['img[data-qa="gameBackgroundImage#heroImage#image-no-js"]','src']
                                }
                }

                
    
    runner = CrawlerRunner(settings=settings)
    runner.crawl(GeneralScraper, scrape_settings=scr_settings)


@run_in_reactor    
def testscrape(scr_settings):
    print("----------------Scraping Started---------------------")
    configure_logging()

    settings = get_project_settings()   

    settings['USER_AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    settings['FEEDS'] = {f'.\\datafolder\\download.json': {'format': 'json', 'overwrite': 'true'}}
    settings['ITEM_PIPELINES'] = {
        
    }   

    playstation = {  'start_url': 'https://store.playstation.com/nl-nl/pages/browse/1',
                'item_links': True,
                'item_css': '//a[@class="psw-link psw-content-link"]',
                'next_page_url': '//button[@data-qa="ems-sdk-grid#ems-sdk-top-paginator-root#next"]',
                'next_page_url_add': 'value',
                'multiple_pages': True,
                'scrape_json': False,
                'attributes':{'title': 'h1.psw-m-b-5',
                                'price': 'span[data-qa="mfeCtaMain#offer0#finalPrice"]'}
                }

    NHL = {     'start_url': 'https://www.scrapethissite.com/pages/forms/?page_num=1',
                'item_links' : False,
                'item_css': '//tr[@class="team"]',
                'scrape_json': False,
                'multiple_pages': True,
                'next_page_url': '//a[contains(@aria-label, "Next")]',
                'next_page_url_add': 'href',
                'attributes': {'name': '//td[@class="name"]',
                                    'year': '//td[@class="year"]',
                                    'wins': '//td[@class="wins"]',
                                    'losses': '//td[@class="losses"]'}
    }

    books = {          'start_url': 'https://books.toscrape.com/catalogue/page-1.html',
                        'item_links' : True,
                        'item_css': 'div[class=image_container] > a',
                        'scrape_json': False,
                        'multiple_pages': True,
                        'next_page_url': 'li[class=next] > a',
                        'next_page_url_add': 'href',
                        'attributes': {'title': '//h1',
                                            'price': '//div[@class="col-sm-6 product_main"]/p[@class="price_color"]'}
                        }

    
    runner = CrawlerRunner(settings=settings)
    # dispatcher.connect(spider_closed_action, signals.spider_closed)
    runner.crawl(GeneralScraper, scrape_settings=scr_settings)


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

# def process_scrape_settings(country_name):
#     json = {'shortcode' : country_name}
#     return json

  



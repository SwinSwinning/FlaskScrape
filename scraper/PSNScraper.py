import scrapy
from scrapy import signals
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlsplit, urlunsplit, urljoin
import json

from scraper.ScraperHelper import xpath_or_css, get_base_url, is_xpath


class PSNScraper(scrapy.Spider):
    name = 'PSNscraperspider'

    def __init__(self, *args, **kwargs):
        super(PSNScraper, self).__init__(*args, **kwargs)
        self.shortcode = self.scrape_settings["shortcode"]
        print(self.shortcode)
        self.start_urls = [f'https://store.playstation.com/{self.shortcode}/pages/browse/']
        self.base_url = get_base_url(self.start_urls[0])


    # link_extractor = LinkExtractor(restrict_css='a.psw-link.psw-content-link')
    link_extractor = LinkExtractor(restrict_xpaths='//a[@class="psw-link psw-content-link"]')
    

    def parse(self, response):
        next_page_selector = 'button[data-qa="ems-sdk-grid#ems-sdk-top-paginator-root#next"]::attr(value)'
        next_page_number = response.css(next_page_selector).get()
        next_page_path = urljoin(self.base_url, next_page_number)

        if int(next_page_number) < 2: # Uncomment to scrape all
            yield scrapy.Request(next_page_path)
       
        for item_link in self.link_extractor.extract_links(response):
            print(item_link)
            item = {} # Create a custom item class object
            request = Request(item_link.url, callback=self.parse_page2)
            request.meta['item'] = item
            yield request

    def parse_page2(self, response):
        item = response.meta['item']
        url = response.url
        get_id = lambda url: url.rsplit('/', 1)[-1] if '/' in url else None

        item['id'] = get_id(url)
        item['price'] = response.css('span[data-qa="mfeCtaMain#offer0#finalPrice"]::text').get()
        item['title'] = response.css('h1.psw-m-b-5::text').get()
        item['imglink'] = response.css('img[data-qa="gameBackgroundImage#heroImage#image-no-js"]::attr(src)').get()      

        item['link'] = url
               

        yield item


class PSNCountryScraper(scrapy.Spider):
    name = 'psncountryspider'

    def __init__(self, *args, **kwargs):
        super(PSNCountryScraper, self).__init__(*args, **kwargs)
        self.start_url = self.scrape_settings["start_url"]
        self.base_url = get_base_url(self.start_url)
        # self.link_type = self.scrape_settings["link_type"]
        self.item_selector = self.scrape_settings['item_css']
        self.contain_item_links = self.scrape_settings['item_links']
        self.multiple_pages = self.scrape_settings['multiple_pages']
        self.scrape_json = self.scrape_settings['scrape_json']
        self.attrs_to_scrape = self.scrape_settings['attributes_dict']


    def start_requests(self):
         yield scrapy.Request(f'{self.start_url}')


    def parse(self, response):
        # This part handles the pagination and crawling through all the pages:
        if self.multiple_pages:
            print("multiple pages-------------------------------------------------------------------------")
            selector = self.scrape_settings["next_page_url"]
            selector += f'::{self.scrape_settings["next_page_url_add"]}'
            path = response.css(selector).get()
           
            combined = urljoin(self.base_url, path)
            yield scrapy.Request(combined)

        # This part handles the crawling of the individual items and if needed extract data from itempages.
        if self.contain_item_links:
            print("Item Links-------------------------------------------------------------------------")
            # if site has item links that need to be accessed, create LinkExtractor Object to help extract item links.
            # ...determine whether the item selector is xpath or css.
            link_extractor =  LinkExtractor(restrict_css=self.item_selector)

            for item_link in link_extractor.extract_links(response):  #..create requests for each item link found on page.
                item = {}
                request = Request(item_link.url,
                                  callback=self.parse_page2,
                                  cb_kwargs={ 'item': item })
                yield request
        
        # If the data to scrape is found in JSON / Dict format on the page
        elif self.scrape_json:
            print("Scrape JSON data -------------------------------------------------------------------------")

            res = response.xpath(self.item_selector).get()
            text_to_find = '"translations":'
            start = res.find(text_to_find)+len(text_to_find)
            end = res[1:].find('<')
            countryJson  = res[start:end]

            json_data = json.loads(countryJson)
    
            country_codes =[]
            id_codes = []

            find_countr = "msgid_country_"
            find_countr_code = "msgid_language_"
            
            # Go through each object in the json file and check the country and country language codes.
            for k,v in json_data.items():
                if k.startswith(find_countr) and len(k) == len(find_countr)+2:
                    country_dict= {}
                 
                    country_dict["country"] = v 
                    country_dict['code'] = k[k.rfind('_')+1:]
                    country_codes.append(country_dict)
           
                elif k.startswith(find_countr_code) and len(k) == 20:
                    id_codes.append(k[k.find('e_')+2:])
                           
            for c in country_codes:
                for y in id_codes:
                    if y[y.rfind("_")+1:] == c["code"]:
                        c["code"] = y.replace('_', '-')

            if len(country_codes) > 0:             
                for country in country_codes:
                    item = country
                    yield item

        else:  # If data to scrape is found on the same page...
            print("No throughlinking -------------------------------------------------------------------------")
            
            rows = response.css(self.item_selector)    

            if len(rows) > 0:             
                for row in rows:
                    print(row)
                    item = {}
                    for k, v in self.attrs_to_scrape.items():
                        item[k] = response.css(row, v).strip()
                    yield item


    def parse_page2(self, response, item):
        # item = response.meta['item']   ---- remove this no longer used as we have added the "item" to the args
        for k,v in self.attrs_to_scrape.items():
            # In case there are multiple selectors given in a list
            if type(v) == list:
                # Loop through each selector...
                for num in range(len(v)):
                    # and see if it gives a valid response
                    if xpath_or_css(response, v[num]):
                        item[k] = xpath_or_css(response, v[num]).strip()
                        break
            else:
                item[k] = xpath_or_css(response, v).strip()
        item['link'] = response.url

        yield item

    
class GeneralScraper(scrapy.Spider):
    name = 'generalscraperspider'

    def __init__(self, *args, **kwargs):
        super(GeneralScraper, self).__init__(*args, **kwargs)
        self.start_url = self.scrape_settings["start_url"]
        self.base_url = get_base_url(self.start_url)
        # self.link_type = self.scrape_settings["link_type"]
        self.item_selector = self.scrape_settings['item_css']
        self.contain_item_links = self.scrape_settings['item_links']
        self.multiple_pages = self.scrape_settings['multiple_pages']
        self.scrape_json = self.scrape_settings['scrape_json']
        self.attrs_to_scrape = self.scrape_settings['attributes']
        self.pages_scraped = 0


    def start_requests(self):
         yield scrapy.Request(f'{self.start_url}')


    def parse(self, response):        
        # This part handles the pagination and crawling through all the pages:
        if self.multiple_pages:
            if self.pages_scraped < 2:
                print("multiple pages-------------------------------------------------------------------------")
                # selector = self.scrape_settings["next_page_url"]
                # selector += f'::attr({self.scrape_settings["next_page_url_add"]})'
                path = xpath_or_css(response, 
                                    self.scrape_settings["next_page_url"], 
                                    self.scrape_settings["next_page_url_add"] ).get()
            
                combined = urljoin(self.base_url, path)
                self.pages_scraped = self.pages_scraped+1 
                yield scrapy.Request(combined)

        # This part handles the crawling of the individual items and if needed extract data from itempages.
        if self.contain_item_links:
            print("Item Links-------------------------------------------------------------------------")
            # if site has item links that need to be accessed, create LinkExtractor Object to help extract item links.
            # ...determine whether the item selector is xpath or css.
            if is_xpath(self.item_selector):
                link_extractor =  LinkExtractor(restrict_xpaths=self.item_selector)
            else:
                link_extractor =  LinkExtractor(restrict_css=self.item_selector)

            for item_link in link_extractor.extract_links(response):  #..create requests for each item link found on page.
                item = {}
                request = Request(item_link.url,
                                  callback=self.parse_page2,
                                  cb_kwargs={ 'item': item })
                yield request
        
        else:  # If data to scrape is found on the same page...
            print("No throughlinking -------------------------------------------------------------------------")
            
            rows = xpath_or_css(response, self.item_selector)  
            rows1 = response.xpath(self.item_selector)

            if len(rows) > 0:             
                for row in rows:
                    print(row)
                    item = {}
                    for k, v in self.attrs_to_scrape.items():
                        print(k, v)                   
                        item[k] = xpath_or_css(row, v, "text").get().strip()
                    yield item


    def parse_page2(self, response, item):
        for k,v in self.attrs_to_scrape.items():
            item[k] = xpath_or_css(response, v).get().strip()
        item['link'] = response.url
        yield item
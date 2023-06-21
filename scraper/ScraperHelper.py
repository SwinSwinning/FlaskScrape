from urllib.parse import urlsplit, urlunsplit

def get_base_url(url, urltype='std'):
    split_url = urlsplit(url)
    if urltype == 'std':
        return urlunsplit((split_url[0],split_url[1],split_url[2].replace('1', '{}'), '',''))
    return urlunsplit((split_url[0], split_url[1], '', '', ''))

def xpath_or_css(response, selector, add=None):
    attr_name_to_scrape = add
    if selector.startswith('./'):
        selector = selector[1:]
    if selector.startswith('/'):
        if attr_name_to_scrape == 'text':
            selector += '/text()[normalize-space()]'       
        elif attr_name_to_scrape:
            selector += f'/@{attr_name_to_scrape}'
            print(selector)

        # Add a '.' in front of the xpath selector, otherwise the iteration will only return the first iter
        return response.xpath(f'.{selector}')
    else:
        selector += f'::attr({attr_name_to_scrape})'
        # selector += f'::attr{attr_name_to_scrape}'

        return response.css(selector)
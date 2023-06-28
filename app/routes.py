import json
from app import app
from app.tasks import run_scrape, run_countries_scrape, get_country_list, run_scrape_new, testscrape
from ftplib import FTP
import creds

import os
from app.forms import ScrapeForm, MulAttrForm, AttributeForm

from flask import send_file, jsonify, redirect, flash, url_for, render_template, request, session


@app.route("/", methods = ['GET'])
@app.route("/index")
def index():
    return render_template('index.html')

@app.route('/upload', methods = ['POST', 'GET'])
def upload_json_to_ftp():

    results= [] 
    # Load the countries.json file to get all the country codes. 
    with open('.\\datafolder\\countries.json') as json_file:
        country_data = json.load(json_file)
    country_codes = [item["code"] for item in country_data]

    # Connect to the FTP server
    ftp = FTP(creds.ftp_host)  
    ftp.login(user=creds.ftp_username, passwd=creds.ftp_password) 
    # Change to the remote FTP directory
    ftp.cwd('/ScrapeFiles')

    # upload the countries.json file.
    try:
        local_file_path = os.path.join(os.getcwd(), f'.\\datafolder\\countries.json')
        with open(local_file_path, 'rb') as f:
            # Get the filename from the local file and upload it to FTP server
            filename = os.path.basename(local_file_path)
            ftp.storbinary(f'STOR {filename}', f)                     
            # Return a success message
            results.append(f'File {filename} uploaded to FTP server.')
    except Exception as e:
        results.append(f'error uploading countries.json : {e}')
        
    # Upload the individual gamelists per country.
    for c in country_codes:
        try:
            local_file_path = os.path.join(os.getcwd(), f'.\\datafolder\\psngames-{c}.json')
            with open(local_file_path, 'rb') as f:
                # Get the filename from the local file and upload it to FTP server
                filename = os.path.basename(local_file_path)
                ftp.storbinary(f'STOR {filename}', f)        
                # Return a success message
                results.append(f'File {filename} uploaded to FTP server.')
        except Exception as e:
            results.append(f"something went wrong with {c} : {e}")
    ftp.quit()
    return results     

@app.route('/download', methods = ['POST', 'GET'])
def download_json():

    country_shortcode = request.form.get('selected_value')
    file_path = os.path.join(os.getcwd(), f'.\\datafolder\\psngames-{country_shortcode}.json')
    return send_file(file_path, as_attachment=True)

@app.route('/json', methods = ['POST', 'GET'])
def get_json_data():
    country_shortcode = request.form.get('display_selected')
    json_path = os.path.join(os.getcwd(), f'.\\datafolder\\psngames-{country_shortcode}.json')
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    return jsonify(data)


@app.route('/test', methods = ['POST', 'GET'])
def test():    
    form = ScrapeForm()
    if form.validate_on_submit():
        num_of_attrs = form.num_of_attrs.data
        attribs = {}
        for i in range(num_of_attrs):
            name = f'attr{i+1}_name'
            val = f'attr{i+1}_val'
            attribs[form[name].data] = form[val].data


        settings = {'start_url': form.start_url.data, 
                    'item_css': form.item_url.data,                    
                    'next_page_url' : form.next_page_url.data,
                    'scrape_json': False,
                    'item_links' : True, 
                    'multiple_pages': True,
                    'next_page_url_add': 'value',
                    'attributes' : attribs
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
    
        run_scrape_new(settings)
        return "hi"
   
    return render_template('gen.html', form=form)

@app.route('/scrape', methods = ['POST', 'GET'])
def scrape():
    country_data = get_country_list()           
    return render_template('scrape.html', country_options=country_data)

@app.route('/general', methods = ['POST', 'GET'])
def scrapegen():
    form = ScrapeForm()
    if form.validate_on_submit():
        session["export"] = {'start_url': form.start_url.data, 'item_url': form.item_url.data,
                             'num_of_attrs': form.num_of_attrs.data, 'next_page_url' : form.next_page_url.data
                             }
        flash(session["export"])
        
       
        return redirect(url_for('general2'))
    return render_template('gen.html', form=form)

@app.route('/general2', methods = ['POST', 'GET'])
def general2():
    exp_settings = session.get('export')
    num_of_attrs = exp_settings['num_of_attrs']
    attrs = [{} for i in range(num_of_attrs)]
    form = MulAttrForm(attributes=attrs)
    # form2 = ScrapeForm()
    if form.validate_on_submit():
        attribs = { entry.fieldname.data: entry.selector_code.data for entry in form.attributes}
        settings = { 'start_url' : exp_settings['start_url'], 
                      'item_url' : exp_settings['item_url'],          
                      'next_page_url' : exp_settings['next_page_url'],
                        'attributes_dict': attribs
                        
        }

        flash('Settings in Session')
        return redirect(url_for('scrape_countries') )
        # return render_template('countries.html')  
    return render_template('gen2.html', form=form)       


@app.route('/data', methods = ['POST', 'GET'])
def data():
    country_data = get_country_list()           
    return render_template('data.html', country_options=country_data)         
   
@app.route('/countries', methods=['GET'])
def scrape_countries():
    run_countries_scrape()
    return render_template('countries.html')

@app.route('/run_scrape')
def startscrape():
    country_shortcode = next(iter(request.args))
    run_scrape(country_shortcode)
    return "Scraping now"
   

@app.route('/gen')
def start_gen_scrape():
    # scr_settings = next(iter(request.args))
    # run_scrape_new(scr_settings)
    run_scrape('en-ie')
    return "Scraping general now"
import json
from pathlib import Path
from app import app
from app.tasks import run_countries_scrape, get_country_list, PSNscrape, general_scrape, testscrape
from ftplib import FTP
import creds

import os
from app.forms import ScrapeForm

from flask import send_file, jsonify, redirect, flash, url_for, render_template, request, session


@app.route("/", methods = ['GET'])
@app.route("/index")
def index():
    return render_template('index.html')

@app.route('/upload', methods = ['POST', 'GET'])
def upload_json_to_ftp():

    results= [] 
    # Load the countries.json file to get all the country codes. 
    with open(Path('./datafolder/countries.json')) as json_file:
        country_data = json.load(json_file)
    country_codes = [item["code"] for item in country_data]

    # Connect to the FTP server
    ftp = FTP(creds.ftp_host)  
    ftp.login(user=creds.ftp_username, passwd=creds.ftp_password) 
    # Change to the remote FTP directory
    ftp.cwd('/ScrapeFiles')

    # upload the countries.json file.
    try:
        local_file_path =  Path('./datafolder/countries.json')
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
            local_file_path =  Path(f'./datafolder/psngames-{c}.json')
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
    file_path = os.path.join(os.getcwd(), Path(f'./datafolder/psngames-{country_shortcode}.json'))
    return send_file(file_path, as_attachment=True)

@app.route('/json', methods = ['POST', 'GET'])
def get_json_data():
    country_shortcode = request.form.get('display_selected')
    json_path = Path(f'./datafolder/psngames-{country_shortcode}.json')
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    return jsonify(data)


@app.route('/scrape', methods = ['POST', 'GET'])
def scrape():
    country_data = get_country_list() 
    if len(country_data) == 1:
        flash("No Country information found. Scrape the Countries first.", "error")           
    return render_template('scrape.html', country_options=country_data)

@app.route('/general', methods = ['POST', 'GET'])
def scrapegen():
    form = ScrapeForm()
    if form.validate_on_submit():
        num_of_attrs = form.num_of_attrs.data
        attribs = {}
        for i in range(num_of_attrs):
            name = f'attr{i+1}_name'
            val = f'attr{i+1}_val'
            add = f'attr{i+1}_add'
            attribs[form[name].data] = [form[val].data, form[add].data]


        settings = {'start_url': form.start_url.data, 
                    'item_css': form.item_url.data,                    
                    'next_page_url' : form.next_page_url.data,
                    'next_page_url_add': form.next_page_url_add.data,
                    'attributes' : attribs
                             }

    
        general_scrape(settings)
        flash(f"Scraping {settings['start_url']} started.")
        return redirect(url_for("index"))   
    return render_template('gen.html', form=form)
  


@app.route('/data', methods = ['POST', 'GET'])
def data():
    country_data = get_country_list()           
    return render_template('data.html', country_options=country_data)         
   
@app.route('/countries', methods=['GET'])
def scrape_countries():
    run_countries_scrape()
    return render_template('countries.html')

@app.route('/run_scrape', methods =['GET', 'POST'])
def startscrape():
    if request.method == 'POST':
        country_shortcode =request.form.get("sform")
        PSNscrape(country_shortcode)
        flash(f"Scraping PSN data for {country_shortcode} now")
    return redirect(url_for("scrape"))
   
@app.route('/test', methods=['GET'])
def test_scrape():
    testscrape()
    return "testScrape"
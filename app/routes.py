import json
from app import app
from app.tasks import run_scrape, run_countries_scrape, get_country_list, run_scrape_new
from ftplib import FTP
import creds

import os

from flask import send_file, jsonify, redirect, url_for, render_template, request


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

@app.route('/download', methods = ['GET'])
def download_json():
    file_path = os.path.join(os.getcwd(), 'psngames-en-ie.json')
    return send_file(file_path, as_attachment=True)

@app.route('/data', methods=['GET'])
def get_data():
    json_path = os.path.join(os.getcwd(), '.\\datafolder\\psngames-en-ie.json')
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    return jsonify(data)


@app.route('/scrape', methods = ['POST', 'GET'])
def scrape():
    country_data = get_country_list()    
    print(get_country_list())         
    return render_template('scrape.html', country_options=country_data)
   

@app.route('/run_scrape')
def startscrape():
    country_shortcode = next(iter(request.args))

    run_scrape(country_shortcode)
    return "Scraping now"
   
@app.route('/countries', methods=['GET'])
def scrape_countries():
    run_countries_scrape()
    return "getting countries"

@app.route('/gen')
def start_gen_scrape():
    run_scrape_new()
    return "Scraping general now"
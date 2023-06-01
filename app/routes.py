import json
from app import app
from app.tasks import run_scrape, scrape_countries
from ftplib import FTP

import os

from flask import send_file, jsonify, redirect, url_for, render_template, request


@app.route("/", methods = ['GET'])
@app.route("/index")
def index():
    return render_template('index.html')

@app.route('/upload', methods = ['POST', 'GET'])
def upload_json_to_ftp():
    # Open the local JSON file
    results= [] 
    country_codes = ["en-ie", "en-th", "nl-nl"]
    # Connect to the FTP server
    ftp = FTP('ftpupload.net')
    ftp.login(user='b16_24575753', passwd='W8woordbyet')
    # Change to the remote FTP directory
    ftp.cwd('/ScrapeFiles')

    for c in country_codes:
        try:
            local_file_path = os.path.join(os.getcwd(), f'psngames-{c}.json')
            with open(local_file_path, 'rb') as f:
                # Get the filename from the local file and upload it to FTP server
                filename = os.path.basename(local_file_path)
                ftp.storbinary(f'STOR {filename}', f)
                # Close the FTP connection
                
                # Return a success message
                results.append(f'File {filename} uploaded to FTP server.')
        except Exception as e:
            results.append(f"something went wrong with {c} : {e}")
    ftp.quit()
    return results     

@app.route('/download', methods = ['GET'])
def download_json():
    file_path = os.path.join(os.getcwd(), 'psngames.json')
    return send_file(file_path, as_attachment=True)

@app.route('/data', methods=['GET'])
def get_data():
    json_path = os.path.join(os.getcwd(), 'psngames.json')
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    return jsonify(data)


@app.route('/scrape', methods = ['POST', 'GET'])
def scrape():
    return render_template('scrape.html')

@app.route('/run_scrape')
def startscrape():
    country_shortcode = next(iter(request.args.keys()))
    print(country_shortcode)
    run_scrape(country_shortcode)
    return "Scraping now"
   
@app.route('/countries', methods=['GET'])
def get_countries():
    scrape_countries()
    return "getting countries"

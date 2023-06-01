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
    local_file_path = os.path.join(os.getcwd(), 'psngames.json')
    with open(local_file_path, 'rb') as f:
        # Connect to the FTP server
        ftp = FTP('ftpupload.net')
        ftp.login(user='b16_24575753', passwd='W8woordbyet')
        # Change to the remote FTP directory
        ftp.cwd('/ScrapeFiles')
        # Get the filename from the local file and upload it to FTP server
        filename = os.path.basename(local_file_path)
        ftp.storbinary(f'STOR {filename}', f)
        # Close the FTP connection
        ftp.quit()
        # Return a success message
    return f'File {filename} uploaded to FTP server.'

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
    country_name = request.args.get()
    print(country_name)
    #  run_scrape(country_name)
    return "Scraping now"
   
@app.route('/countries', methods=['GET'])
def get_countries():
    scrape_countries()
    return "getting countries"

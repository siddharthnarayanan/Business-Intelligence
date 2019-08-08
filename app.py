from flask import Flask, render_template, g, Response, request, redirect, url_for, render_template, flash, send_file,jsonify
#from json import dumps
#from models import Populate_Data_Model as pdm

# from models import Conversation, ReshapeTree, Semantic_CoreNLP, Intent_Classifier, Transcribe, ReadText, SentimentIntensity
# from werkzeug.utils import secure_filename

#import os
#import sys
#from ctypes import*
#import ctypes
# from pymongo import MongoClient
#import json
# from bson import json_util
# from bson.json_util import dumps
from flask import send_file
#import os
#import pandas as pd


app = Flask(__name__)

# UPLOAD_FOLDER = './uploads'
# ALLOWED_EXTENSIONS = set(['wav','mp3','txt','csv'])

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.secret_key = "super secret key"

@app.route("/")
def index():
    return render_template("Summary_KPI.html")

@app.route("/main_page")
def main_page():
    return render_template("Summary_KPI.html")

@app.route("/upload")
def upload():
	return render_template("Upload.html")

@app.route("/digitalized")
def digitized():
	return render_template("Digitalized.html")

	
@app.route("/bi_reporting")
def syndicated_loan():
	return render_template("BI_Reporting_v1.html")


@app.route("/mortgage")
def mortgage():
	return render_template("BIReporting2_mortgage.html")
	

@app.route("/isda")
def isda():
	return render_template("BIReporting2_isda.html")
	

@app.route("/table_styles")
def table_styles():
	return render_template("tableStyles.html")
	
	
@app.route("/bi_reporting")
def bi_reporting():
	return render_template("BIReporting2_signature.html")
	
@app.route("/fallback_language")
def fallback_language():
	return render_template("Fallback_Language.html")

@app.route("/non_fallback_language")
def non_fallback_language():
	return render_template("Non_Fallback_Language.html")


@app.route("/fallback_isda")
def fallback_language_isda():
	return render_template("Fallback_Language_isda.html")	
	
@app.route("/fallback_mortgage")
def fallback_language_mortgage():
	return render_template("Fallback_Language_mortgage.html")	
	
@app.route("/fallback_language_detail")
def fallback_language_detail():
	return render_template("Fallback_Language_Detail.html")

@app.route("/field_tagger")
def field_tagger():
	return render_template("Field_Tagger.html")

@app.route("/data_model")
def data_model():
	return render_template("Data_Model.html")

@app.route("/non_fallback_language_detail")
def non_fallback_language_detail():
	return render_template("Non_Fallback_Language_Detail.html")	


@app.route("/ocr_processed", methods=['GET','POST','PUT'])
def ocr_processed():
	return render_template("OCR_display.html")

@app.route("/classification")
def classify():
	return render_template("Classification.html")

@app.route("/exceptionmgmt")
def exception_mgmt():
	return render_template("ExceptionMgmtPopup.html")


@app.route("/nav_bar")
def nav_bar():
	return render_template("eybi_nav.html")

	
@app.route("/contract_lifecycle")
def contract_lifecycle():
	return render_template("ContractLifecycleManagement.html")

   
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=7000,debug=True)

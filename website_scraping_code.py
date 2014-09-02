# Bethany's Formulaic Website Scraping Code.
# Many online records have formulaic URLs based on a unique identifier (especially government records). Often, you can download a 
# CSV with some of the information, including the unique identifier, but you cannot download the extended description. 
# This code will allow you to import a tab-delineated file, scrape specified sections from the websites, and then add the information
# back into your file.

# Functions to define: 1) open CSV, 2) formulate URLs from uniqueIDs in CSV, 3) search & scrape
# and add to dictionary. 4) Write dictionary to file
# I originally tried to use lxml, but it was a big pain in the neck so I used BeautifulSoup instead. 
# A friend also recommended I try Scrapepy, because he says "it is a true web crawler instead of just a parser. I may try
# that in the future.

import bs4
from bs4 import BeautifulSoup
import requests
import time
import csv

def createListFromTSV(tsvFile):
	with open(tsvFile,"rU") as f:
		fileReader = csv.DictReader(f,delimiter='\t')
#		print type(fileReader)
		fileList = []
		for line in fileReader:
			fileList.append(line)
		return fileList
#		print fileList

def createHeaderList(tsvFile):
	with open(tsvFile,"rU") as myFile:
		lines = myFile.read().split("\n")
		if lines <2:
			lines = myFile.read().split("\r")
		headers = lines[0].split("\t")
		return headers

def writeDictToTSV(myList, destFile, tsvFile, newColumnName):
	headers = createHeaderList(tsvFile)
	headers.append('URL')
	headers.append(newColumnName)
#	print headers
	with open(destFile,"w") as outfile:
		destination = csv.DictWriter(outfile,headers,delimiter='\t')
		destination.writeheader()
		for thing in myList:
			destination.writerow(thing)

def formulateURLList(fileList, uniqueIDColumnName, urlFormulaPrefix, urlFormulaSuffix=''):
	for entry in fileList: # fileList is a list of dicts
		uniqueID = entry.get(uniqueIDColumnName)
		URL = urlFormulaPrefix+uniqueID+urlFormulaSuffix
		entry['URL'] = URL
	return fileList
	
	def scrape(URL, section):
	'''string --> string
	Scrapes data from a given section in a given URL. Sections must be 
	written in html format, i.e. <div class="wrapper_std"> or <h3 class="currentVersion">
	'''
	webpage = requests.get(URL, allow_redirects=False)
	soup = BeautifulSoup(webpage.text)
#	print soup
	if "=" in section:
		htmlSection = section[1:section.find("=")].split(" ")
		htmlTagPrefix = htmlSection[0]
		htmlTagSuffix = htmlSection[1]
		htmlTag = section[section.find("=")+1:]
		response = []
		searchSection = '{0}, {1}_={2}'.format(htmlTagPrefix, htmlTagSuffix, htmlTag)
#		print (searchSection)
		for part in soup.find_all(searchSection):
			response.append(part)
	else:
		response = []
		for sect in soup.findAll(lambda tag:tag.name.lower()==section):
			response.append(sect)
	return response
	time.sleep(1)


def scrapeUpdateDict(**kwargs):
	#if you want to add a default, you can write variable = kwargs.get('variable',default) otherwise value is none
	# steps are 1) create fileDict, 2) create urlDict, 3) scrape data, 
	# 4) add data to newColumnName in fileDict, 5) write info/new info to csv_file or csv_file_destination
	htmlSection = kwargs.get('htmlSection')
	tsv_file = kwargs.get('tsv_file')
	uniqueIDColumnName = kwargs.get('uniqueIDColumnName')
	newColumnName = kwargs.get('newColumnName')
	urlFormulaPrefix = kwargs.get('urlFormulaPrefix')
	urlFormulaSuffix = kwargs.get('urlFormulaSuffix','')
	tsv_file_destination = kwargs.get('tsv_file_destination','tsv_file')
	headers = kwargs.get('headers')
# add other option to formulate URL Dict not from generic way (i.e. for bill summary URLs)	
	kwargs['headers'].append('URL')
	kwargs['headers'].append(newColumnName)
	fileList = createListFromTSV(tsv_file)
	fileList = formulateURLList(fileList, uniqueIDColumnName,urlFormulaPrefix, urlFormulaSuffix)
#	print fileList
	for item in fileList:
		print item.get('URL')
		newInfo = scrape(item.get('URL'), htmlSection)
#		print newInfo
		item[newColumnName] = newInfo
	writeDictToTSV(fileList, tsv_file_destination, tsv_file, newColumnName)
		
NTSBKwargsDict = { 'htmlSection' : 'p', 
'tsv_file' : '/Users/bethanylquinn/Desktop/Pyscripts/NTSB_Test.txt', 
'uniqueIDColumnName' : 'Event Id', 'newColumnName' : 'Description',
'urlFormulaPrefix' : 'http://www.ntsb.gov/aviationquery/brief.aspx?ev_id=',
'urlFormulaSuffix' : '&key=1',
'tsv_file_destination' : 'NTSBTestResult2.txt'}

NTSBKwargsDict['headers']=createHeaderList('/Users/bethanylquinn/Desktop/Pyscripts/NTSB_Test.csv')

webpage = requests.get('http://www.ntsb.gov/aviationquery/brief.aspx?ev_id=20140408X84430&key=1', allow_redirects=False)
soup = BeautifulSoup(webpage.text)
print(soup.prettify())

scrapeUpdateDict(**NTSBKwargsDict)



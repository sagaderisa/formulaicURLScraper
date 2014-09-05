# Bethany's Formulaic Website Scraping Code.
# Many online records have formulaic URLs based on a unique identifier (especially government records). Often, you can download a 
# CSV with some of the information, including the unique identifier, but you cannot download the extended description. 
# This code will allow you to import a tab-delineated file, scrape specified sections from the websites, and then add the information
# back into your file.

# I originally tried to use lxml, and then Beautiful Soup, (by using html tags to denote which sections to scrape), 
# but because the HTML wasn't consistent, I finally went with regular expressions, which allows me to do a text-based approach.
# A friend also recommended I try Scrapepy, because he says "it is a true web crawler instead of just a parser. I may try
# that in the future.


# Functions to define: 1) open CSV, 2) formulate URLs from uniqueIDs in CSV, 3) search & scrape
# and add to dictionary. 4) Write dictionary to file


import requests # Requests interacts with the web and pulls data from websites.
import time # Time allows you to delay your requests so that you don't bombard the other person's server
import csv # CSV is a module that helps with file handling
import re # re stands for "regular expressions" and it allows you to recognize a pattern and pull information from it

def createListFromTSV(tsvFile):
	'''This function takes a tab-delineated file (tsvFile) and returns a list of dictionaries.'''
	with open(tsvFile,"rU") as f:
		fileReader = csv.DictReader(f,delimiter='\t')
#		print type(fileReader)
		fileList = []
		for line in fileReader:
			fileList.append(line)
		return fileList
#		print fileList

def createHeaderList(tsvFile):
	'''This function creates a list of headers from a tab-delineated file (tsvfile).'''
	with open(tsvFile,"rU") as myFile:
		lines = myFile.read().split("\n")
		if lines <2:
			lines = myFile.read().split("\r")
		headers = lines[0].split("\t")
		return headers

def writeDictToTSV(myList, destFile, tsvFile, newColumnName):
	'''This function writes a list of dictionaries to a tsvFile.'''
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
	'''This creates a list of URLs based on a list of unique identifiers.'''
	for entry in fileList: # fileList is a list of dicts
		uniqueID = entry.get(uniqueIDColumnName)
		URL = urlFormulaPrefix+uniqueID+urlFormulaSuffix
		entry['URL'] = URL
	return fileList



def scrape(URL, startQuote, endQuote):
	'''string --> string
	Scrapes data from a given section in a given URL. Currently, you need to write
	startQuote and endQuote in regular expression-friendly format (i.e. put \ before 
	some characters, \s instead of space, etc.).
	'''
	time.sleep(1)
	webpage = requests.get(URL, allow_redirects=False).text
#	print webpage
	searchStr = str(startQuote + '(.+)' + endQuote)
	scraping = re.search(searchStr,webpage)
	# add try here instead of this way, also add "source\sof\sthis\sinformation\."
	try:
		return scraping.group(1).encode('utf-8')
	except AttributeError:
		print '''Scraping program didn't work for {0}. Most likely, this instance 
		varies from the page/formula you entered. Try going to the URL manually.'''.format(URL)
		return '''The program was unable to scrape this record. Most likely, this instance 
		varies from the page/formula you entered.  Try going to the URL manually.
		'''
#	if scraping == None:
#		print "Scraping program couldn't find the information for {0}.".format(URL)
#	return scraping.group(1)
#	print scraping


def scrapeUpdateDict(**kwargs):
	'''This is the core function of this module. If you are trying to scrape data from a 
	series of websites with formulaic URLs based on a unique identifier (government sites are 
	commonly formatted this way), put them in a tab-delineated file (you can frequently 
	download some but not all of the information about a given set of government information). 
	This function will read the tab-delineated file, pull out the unique identifier, formulate the URL, 
	and scrape the data you specify from the website. (In order to do this, you'll need to know 
	what the text or html is around the text you want to scrape.)
	'''
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
	startQuote = kwargs.get('startQuote')
	endQuote = kwargs.get('endQuote')
# add other option to formulate URL Dict not from generic way (i.e. for bill summary URLs)	
	kwargs['headers'].append('URL')
	kwargs['headers'].append(newColumnName)
	fileList = createListFromTSV(tsv_file)
	fileList = formulateURLList(fileList, uniqueIDColumnName,urlFormulaPrefix, urlFormulaSuffix)
#	print fileList
	for item in fileList:
		print item.get('URL')
		newInfo = scrape(item.get('URL'), startQuote, endQuote)
#		print newInfo
		item[newColumnName] = newInfo
	writeDictToTSV(fileList, tsv_file_destination, tsv_file, newColumnName)

NTSBTestKwargsDict = { 'startQuote' : 'to\sprepare\sthis\saircraft\saccident\sreport\.', 'endQuote' : 'Index\sfor',
'tsv_file' : '/Users/bethanylquinn/Desktop/Pyscripts/NTSB_Test.txt', 
'uniqueIDColumnName' : 'Event Id', 'newColumnName' : 'Description',
'urlFormulaPrefix' : 'http://www.ntsb.gov/aviationquery/brief.aspx?ev_id=',
'urlFormulaSuffix' : '&key=1',
'tsv_file_destination' : 'NTSBTestResult3.txt'}

NTSBTestKwargsDict['headers']=createHeaderList('/Users/bethanylquinn/Desktop/Pyscripts/NTSB_Test.txt')

NTSBKwargsDict = { 'startQuote' : 'to\sprepare\sthis\saircraft\saccident\sreport\.', 'endQuote' : 'Index\sfor',
'tsv_file' : '/Users/bethanylquinn/Desktop/Pyscripts/NTSB_ramp_accidents.txt', 
'uniqueIDColumnName' : 'Event Id', 'newColumnName' : 'Description',
'urlFormulaPrefix' : 'http://www.ntsb.gov/aviationquery/brief.aspx?ev_id=',
'urlFormulaSuffix' : '&key=1',
'tsv_file_destination' : 'NTSB_ramp_accident_info.txt'}

NTSBKwargsDict['headers']=createHeaderList('/Users/bethanylquinn/Desktop/Pyscripts/NTSB_ramp_accidents.txt')

scrapeUpdateDict(**NTSBKwargsDict)

# This next bit was my first attempt to write a scrape function. It was based on 
# lxml, which is a huge pain in the ass. Use BeautifulSoup instead.


# Add input to format in FAASearchURL and define uniqueColumnName
# FAASearchURL = 'http://www.asias.faa.gov/pls/apex/f?p=100:18:0::NO::AP_BRIEF_RPT_VAR:'
# FAA_Test_File = '/Users/bethanylquinn/Desktop/Pyscripts/FAA_AIDS_Test.csv'
# NTSBURLPrefix = 'www.ntsb.gov/aviationquery/brief.aspx?ev_id='
# NTSBURLSuffix = '&key=1'


# FAAURLDict = formulateURLDict('/Users/bethanylquinn/Desktop/Pyscripts/FAA_AIDS_Test.csv', 'AIDS Report Number', FAASearchURL)
# print FAAURLDict

# NTSBURLDict = formulateURLDict('/Users/bethanylquinn/Desktop/Pyscripts/NTSB_Test.csv', 'Event Id', NTSBURLPrefix, NTSBURLSuffix)
# print NTSBURLDict

# regular expressions - aircraft\sincident\sreport\.(.+)\<a 
# Dot in regular expressions stands for one character of anything. \. means it's an actual period.
# Parentheses says you actually want to save it. \ means it's actually the character that follows.

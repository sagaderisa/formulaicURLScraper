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

# Here I'm defining a function to import the file as a list of dictionaries. 
# That will keep the original order of the rows in the file, but also allow me to pull 
# information from a given column. I created a method using tab-delineated text file first
# because the first file I was working with had a lot of internal commas, and NTSB used '|' to delineate fields.
# But CSV is more conventional, so I'm in the process of building that in. 


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

def createListFromCSV(csvFile):
	with open(csvFile, "rU") as f:
		fileReader = csv.DictReader(f)
		fileList = []
		for line in fileReader:
			fileList.append(line)
		return fileList

# Here I'm creating a list of headers (column names). This will allow me to put the columns
# back in their original order. Also, I believe some of the DictWriter functions requires a headers list.

def createHeaderList(tsvFile):
	'''This function creates a list of headers from a tab-delineated file (tsvfile).'''
	with open(tsvFile,"rU") as myFile:
		lines = myFile.read().split("\n")
		if lines <2:
			lines = myFile.read().split("\r")
		headers = lines[0].split("\t")
		return headers

def createCSVHeaderList(csvFile):
	with open(csvFile, "rU") as myFile:
		lines = myFile.read().split("\n")
		if lines <2:
			lines = myFile.read().split("\r")
		headers = lines[0].split(",")
		return headers

# Here, I'm writing the list of dictionaries back to the file.

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

def writeDictToCSV(myList, destFile, csvFile, newColumnName):
	'''This function writes a list of dictionaries to a csvFile.'''
	headers = createCSVHeaderList(csvFile)
	headers.append('URL')
	headers.append(newColumnName)
	with open(destFile, "w") as outfile:
		destination = csv.DictWriter(outfile,headers)
		destination.writeheader()
		for thing in myList:
			destination.writerow(thing)

# This function pulls the unique identifiers out of your fileList and then creates URLs based
# on a formula you specify.

def formulateURLList(fileList, uniqueIDColumnName, urlFormulaPrefix, urlFormulaSuffix=''):
	'''This creates a list of URLs based on a list of unique identifiers.'''
	for entry in fileList: # fileList is a list of dicts
		uniqueID = entry.get(uniqueIDColumnName)
		URL = urlFormulaPrefix+uniqueID+urlFormulaSuffix
		entry['URL'] = URL
	return fileList

# This function scrapes the html/text between your startQuote and your endQuote.
# It uses regular expressions, which is kind of finicky. Here's a regular expressions cheat sheet:
# http://regexlib.com/CheatSheet.aspx?AspxAutoDetectCookieSupport=1

def scrape(URL, startQuote, endQuote):
	'''string --> string
	Scrapes data from a given section in a given URL. Currently, you need to write
	startQuote and endQuote in regular expression-friendly format (i.e. put \ before 
	some characters, \s instead of space, etc.).
	'''
	time.sleep(0.5)
	webpage = requests.get(URL, allow_redirects=False).text
#	print webpage
	searchStr = str(startQuote + '(.+)' + endQuote)
#	print type(searchStr)
	scraping = re.search(searchStr,webpage,re.DOTALL)
#	print "webpage: ",webpage
	# add try here instead of this way, also add "source\sof\sthis\sinformation\."
	try:
		return scraping.group(1).encode('utf-8')
	except AttributeError:
		print "Scraping program didn't work for {0}. Most likely, this instance varies from the page/formula you entered. Try going to the URL manually.".format(URL)
		return 'The program was unable to scrape this record. Most likely, this instance varies from the page/formula you entered.  Try going to the URL manually.'
#	if scraping == None:
#		print "Scraping program couldn't find the information for {0}.".format(URL)
#	return scraping.group(1)
#	print scraping

# Here's where it all comes together. 

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

# I wrote a separate function in case you wanted to create your URL list in your excel file.
# Sometimes this is easier when a URL is formulaic but more complicated than prefix + uniqueID + suffix

def csvScrapeUpdateDict(**kwargs):
	'''This is the core function of this module. If you are trying to scrape data from a 
	series of websites with formulaic URLs based on a unique identifier (government sites are 
	commonly formatted this way), put them in a csv file (you can frequently 
	download some but not all of the information about a given set of government information). 
	This function will read the csv file, pull out the unique identifier, formulate the URL, 
	and scrape the data you specify from the website. (In order to do this, you'll need to know 
	what the text or html is around the text you want to scrape.)
	'''
	#if you want to add a default, you can write variable = kwargs.get('variable',default) otherwise value is none
	# steps are 1) create fileDict, 2) create urlDict, 3) scrape data, 
	# 4) add data to newColumnName in fileDict, 5) write info/new info to csv_file or csv_file_destination
	csv_file = kwargs.get('csv_file')
	uniqueIDColumnName = kwargs.get('uniqueIDColumnName')
	newColumnName = kwargs.get('newColumnName')
	urlFormulaPrefix = kwargs.get('urlFormulaPrefix')
	urlFormulaSuffix = kwargs.get('urlFormulaSuffix','')
	csv_file_destination = kwargs.get('csv_file_destination','csv_file')
	headers = kwargs.get('headers')
	startQuote = kwargs.get('startQuote')
	endQuote = kwargs.get('endQuote')
# add other option to formulate URL Dict not from generic way (i.e. for bill summary URLs)	
	print "Headers type before adding new columns is: ",type(headers)
	kwargs['headers'].append('URL')
	kwargs['headers'].append(newColumnName)
#	print "Headers are: ",kwargs['headers']
	print "Headers type after adding new columns: ",type(headers)
	fileList = createListFromCSV(csv_file)
	fileList = formulateURLList(fileList, uniqueIDColumnName,urlFormulaPrefix, urlFormulaSuffix)
	for item in fileList:
		print item.get('URL')
		newInfo = scrape(item.get('URL'), startQuote, endQuote)
#		print newInfo
		item[newColumnName] = newInfo
#	print "fileList is: ",fileList
	writeDictToCSV(fileList, csv_file_destination, csv_file, newColumnName)

def scrapeFromURLList(**kwargs):
	tsv_file = kwargs.get('tsv_file')
	urlColumnName = kwargs.get('urlColumnName')
	newColumnName = kwargs.get('newColumnName')
	tsv_file_destination = kwargs.get('tsv_file_destinaton','tsv_file')
	headers = kwargs.get('headers')
	startQuote = kwargs.get('startQuote')
	endQuote = kwargs.get('endQuote')
	kwargs['headers'].append(newColumnName)
	print "Headers are: ",kwargs['headers']
	fileList = createListFromTSV(tsv_file)
	for item in fileList:
		URL = item.get(urlColumnName)
		newInfo = scrape(URL, startQuote, endQuote)
		item[newColumnName] = newInfo
		print "Item is: ",item
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


FAATestKwargsDict = { 'csv_file' : 'FAA_Test.csv', 
'uniqueIDColumnName' : 'AIDS Report Number',
'newColumnName' : 'Event Remarks', 
'urlFormulaPrefix' : 'http://www.asias.faa.gov/pls/apex/f?p=100:18:0::NO::AP_BRIEF_RPT_VAR:',
'csv_file_destination' : 'FAA_ramp_test_dest_file.csv',
'startQuote' : '<div\sid="narr_text">\s?<br>',
'endQuote' : '</div>\n<HR>\n<div\sid="end_1">END\sREPORT'}

FAATestKwargsDict['headers']=createCSVHeaderList('FAA_Test.csv')
print "FAA Test Headers are: ",FAATestKwargsDict['headers']


FAAKwargsDict = { 'csv_file' : 'FAA_ramp_incidents.csv', 
'uniqueIDColumnName' : 'AIDS Report Number',
'newColumnName' : 'Event Remarks', 
'urlFormulaPrefix' : 'http://www.asias.faa.gov/pls/apex/f?p=100:18:0::NO::AP_BRIEF_RPT_VAR:',
'csv_file_destination' : 'FAA_ramp_dest_file.csv',
'startQuote' : '<div\sid="narr_text">\s?<br>',
'endQuote' : '</div>\n<HR>\n<div\sid="end_1">END\sREPORT'}

FAAKwargsDict['headers']=createCSVHeaderList('FAA_ramp_incidents.csv')



OSHATestKwargsDict = { 'csv_file' : 'OSHATestFile.csv',
'uniqueIDColumnName' : 'Summary NR',
'newColumnName' : 'Accident Description',
'urlFormulaPrefix' : 'https://www.osha.gov/pls/imis/accidentsearch.accident_detail?id=',
'csv_file_destination' : 'OSHATestResult.csv',
'startQuote' : 'WIDTH="99%">\n<tr><td\sclass="blueTen">',
'endQuote': '</td></tr>\n</TABLE>\n</td></tr>\n<tr><td>\n<TABLE\sbgcolor="white"\sborder="0"\scellspacing="1" cellpadding="3"\sWIDTH="99%">\n<tr><td\sclass="blueBoldTen"\svalign="top">Keywords:'
}

OSHATestKwargsDict['headers']=createCSVHeaderList('OSHATestFile.csv')

OSHAKwargsDict = { 'csv_file' : 'OSHAAccidentsNAICS4811_4812_4881.csv',
'uniqueIDColumnName' : 'Summary NR',
'newColumnName' : 'Accident Description',
'urlFormulaPrefix' : 'https://www.osha.gov/pls/imis/accidentsearch.accident_detail?id=',
'csv_file_destination' : 'OSHAAccidentsWithDescriptions_NAICS4811_4812_4881.csv',
'startQuote' : 'WIDTH="99%">\n<tr><td\sclass="blueTen">',
'endQuote': '</td></tr>\n</TABLE>\n</td></tr>\n<tr><td>\n<TABLE\sbgcolor="white"\sborder="0"\scellspacing="1" cellpadding="3"\sWIDTH="99%">\n<tr><td\sclass="blueBoldTen"\svalign="top">Keywords:'
}

OSHAKwargsDict['headers'] = createCSVHeaderList('OSHAAccidentsNAICS4811_4812_4881.csv')


# scrapeUpdateDict(**NTSBTestKwargsDict)

csvScrapeUpdateDict(**FAATestKwargsDict)


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

def createListFromCSV(csvFile,myDelimiter=','):
	with open(csvFile, "rU") as f:
		fileReader = csv.DictReader(f,delimiter=myDelimiter)
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

def createCSVHeaderList(csvFile,myDelimiter=','):
	with open(csvFile, "rU") as myFile:
		lines = myFile.read().split("\n")
		if lines <2:
			lines = myFile.read().split("\r")
		headers = lines[0].split(myDelimiter)
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

def writeDictToCSV(myList, destFile, csvFile, newColumnName='',myDelimiter=','):
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

def formulateBillURLList(file, billNumberColumn='Bill number',myDelimiter=','):
	billFileList = createListFromCSV(file, myDelimiter)
	for record in billFileList:
		billNo = record.get('Bill number')
		billNo = billNo.replace('.','')
		billNo = billNo.replace(' ','')
		billNo = billNo.lower()
		print "Formatted bill number in line 99ish is: ",billNo
		if billNo == '':
			record['CRS Summary'] = 'Bill number needed to get CRS summary.'
		elif billNo[1:3] == 'res':
			record['CRS Summary'] = 'Code pending for resolutions.'
		elif billNo[0] == 's':
			record['URL'] = "https://beta.congress.gov/bill/113th-congress/senate-bill/{0}".format(billNo[1:])
		elif billNo[:2] == 'hr':
			record['URL'] = "https://beta.congress.gov/bill/113th-congress/house-bill/{0}".format(billNo[2:])
		else:
			print "Bill format not recognized. Please try again. (Line 106ish)"
	return billFileList
			
	

# This function scrapes the html/text between your startQuote and your endQuote.
# It uses regular expressions, which is kind of finicky. Here's a regular expressions cheat sheet:
# http://regexlib.com/CheatSheet.aspx?AspxAutoDetectCookieSupport=1

def strToRegEx(string):
	string = string.replace("\\", "\\\\")
	string = string.replace("^","\^")
	string = string.replace("$","\$")
	string = string.replace(".","\.")
	string = string.replace("|","\|")
	string = string.replace("?","\?")
	string = string.replace("*","\*")
	string = string.replace("+","\+")
	string = string.replace("(","\(")
	string = string.replace(")","\)")
	string = string.replace("[","\[")
	string = string.replace("{","\{")
	return string


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
	return scraping.group(1).encode('utf-8')
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

def nameUserKwargs():
	websiteName = raw_input("What is the name of the agency or website you'll be scraping info from? ")
	websiteNameCode = websiteName.replace(" ","_")
	infoType = raw_input("What information will you be scraping? Be as descriptive as possible as other users will be able to scrape this info going forward as well. ")
	infoTypeCode = infoType.replace(" ","_")
	kwargsNewName = websiteNameCode+"_"+infoTypeCode
	return kwargsNewName

def userDefinedScrapeKwargs():
	userKwargs = {}
	fileType = raw_input('''This program only works with CSV files or tab-delineated text files (.txt).
Type "csv" if your file is a csv file and "txt" if your file is a tab-delineated text file. ''')
	if fileType.lower() == 'csv':
		userKwargs['csv_file'] = raw_input("What is the name of your file? ")
		destFile = raw_input("What do you want to call the file you want to dump the information back into? ")
		userKwargs['csv_file_destination'] = destFile
		userKwargs['headers'] = createCSVHeaderList(userKwargs.get('csv_file'))
	elif fileType.lower() == 'txt':
		userKwargs['tsv_file'] = raw_input("What is the name of your file? ")
		destFile = raw_input("What do you want to call the file you want to dump the information back into? ")
		userKwargs['tsv_file_destination'] = destFile
		userKwargs['headers'] = createHeaderList(userKwargs.get('tsv_file'))
	else:
		print "I'm sorry, this program does not accept that type of file."
	# figure out how to loop back to file input questions
	userKwargs['uniqueIDColumnName'] = raw_input("What is the exact name of the column with the unique ID that the URLs are based on? ")
	userKwargs['newColumnName'] = raw_input("What do you want to call the column with the new information? ")
	userKwargs['urlFormulaPrefix'] = raw_input("What is the part of the URL before the unique identifier? ")
	suffixTest = raw_input("Does the URL continue after the unique identifier? (Yes or no) ")
	if suffixTest.lower() == "yes":
		userKwargs['urlFormulaSuffix'] = raw_input("What comes after the unique identifier in the URL? (i.e. what is the suffix) ")
	startQuoteRaw = raw_input("What is the unique phrase (or ideally html) that comes before the information you want to scrape? ")
	userKwargs['startQuote'] = strToRegEx(startQuoteRaw)
	endQuoteRaw = raw_input("What is the name of the unique phrase (or ideally html) that comes after the information you want to scrape? ")
	userKwargs['endQuote'] = strToRegEx(endQuoteRaw)
	print userKwargs
	return userKwargs
	
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
	urlFormulaPrefix = kwargs.get('urlFormulaPrefix','') # only optional if pulling CRS/congress info or if pulling URLs from a file
	urlFormulaSuffix = kwargs.get('urlFormulaSuffix','')
	csv_file_destination = kwargs.get('csv_file_destination','csv_file')
	headers = kwargs.get('headers',[])
	startQuote = kwargs.get('startQuote')
	endQuote = kwargs.get('endQuote')
	alternateStartQuoteList = kwargs.get('alternateStartQuoteList',[])
	alternateEndQuoteList = kwargs.get('alternateEndQuoteList',[])
	myDelimiter = kwargs.get('myDelimiter',',')
	specialURLs = kwargs.get('specialURLs')
	if headers == []:
		kwargs['headers'] = createCSVHeaderList(csv_file, myDelimiter)
# add other option to formulate URL Dict not from generic way (i.e. for bill summary URLs)	
#	print "Headers type before adding new columns is: ",type(headers)
	kwargs['headers'].append('URL')
	kwargs['headers'].append(newColumnName)
#	print "Headers are: ",kwargs['headers']
#	print "Headers type after adding new columns: ",type(headers)
	fileList = createListFromCSV(csv_file, myDelimiter)
	if specialURLs == None:
		fileList = formulateURLList(fileList, uniqueIDColumnName,urlFormulaPrefix, urlFormulaSuffix)
	elif specialURLs == 'Congress CRS':
		fileList = formulateBillURLList(csv_file, uniqueIDColumnName)
	else:
		print "I don't have instructions for that type of URL/file yet. Please try again - current options are None or 'Congress CRS'"
	for item in fileList:
		print "In line 271ish, the URL is:", item.get('URL')
		try:
			newInfo = scrape(item.get('URL'), startQuote, endQuote)
		except requests.exceptions.MissingSchema:
			print "Missing URL in line 283ish."
		except AttributeError:
			print "Attribute error. Moving down the exceptions list in line 281ish"
			print "alternateEndQuoteList's type is {0} and it is: {1}".format(type(alternateEndQuoteList),alternateEndQuoteList)
			for quote in alternateEndQuoteList:
				print "In line 287ish, seeing if alternate quote {0} will work.".format(quote)
				try:
					newInfo = scrape(item.get('URL'), startQuote, quote)
				except:
					newInfo = "Summary could not be scraped for this bill (line 288ish)."
		except: 
			print "Some other error occurred in line 289ish." 
			raise
		if specialURLs == 'Congress CRS':
			newInfo = newInfo.replace('<p>','')
			newInfo = newInfo.replace('</li> <li>','')
			newInfo = newInfo.replace('</p>','')
			newInfo = newInfo.strip()
#		print newInfo
		item[newColumnName] = newInfo
		
#	print "fileList is: ",fileList
	writeDictToCSV(fileList, csv_file_destination, csv_file, newColumnName)

# NEXT STEP: finish function to scrape from user-defined URL list.
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
#		print "Item is: ",item
	writeDictToTSV(fileList, tsv_file_destination, tsv_file, newColumnName)
	
NTSBKwargsDict = { 'startQuote' : 'to\sprepare\sthis\saircraft\saccident\sreport\.', 'endQuote' : 'Index\sfor',
'tsv_file' : '/Users/bethanylquinn/Desktop/Pyscripts/NTSB_ramp_accidents.txt', 
'uniqueIDColumnName' : 'Event Id', 'newColumnName' : 'Description',
'urlFormulaPrefix' : 'http://www.ntsb.gov/aviationquery/brief.aspx?ev_id=',
'urlFormulaSuffix' : '&key=1',
'tsv_file_destination' : 'NTSB_ramp_accident_info.txt'}

NTSBKwargsDict['headers']=createHeaderList('/Users/bethanylquinn/Desktop/Pyscripts/NTSB_ramp_accidents.txt')

FAAKwargsDict = { 'csv_file' : 'FAA_ramp_incidents.csv', 
'uniqueIDColumnName' : 'AIDS Report Number',
'newColumnName' : 'Event Remarks', 
'urlFormulaPrefix' : 'http://www.asias.faa.gov/pls/apex/f?p=100:18:0::NO::AP_BRIEF_RPT_VAR:',
'csv_file_destination' : 'FAA_ramp_dest_file.csv',
'startQuote' : '<div\sid="narr_text">\s?<br>',
'endQuote' : '</div>\n<HR>\n<div\sid="end_1">END\sREPORT'}

FAAKwargsDict['headers']=createCSVHeaderList('FAA_ramp_incidents.csv')

OSHAKwargsDict = { 'csv_file' : 'OSHAAccidentsNAICS4811_4812_4881.csv',
'uniqueIDColumnName' : 'Summary NR',
'newColumnName' : 'Accident Description',
'urlFormulaPrefix' : 'https://www.osha.gov/pls/imis/accidentsearch.accident_detail?id=',
'csv_file_destination' : 'OSHAAccidentsWithDescriptions_NAICS4811_4812_4881.csv',
'startQuote' : 'WIDTH="99%">\n<tr><td\sclass="blueTen">\n',
'endQuote': '\n</td></tr>\n</TABLE>\n</td></tr>\n<tr><td>\n<TABLE\sbgcolor="white"\sborder="0"\scellspacing="1" cellpadding="3"\sWIDTH="99%">\n<tr><td\sclass="blueBoldTen"\svalign="top">Keywords:'
}

OSHAKwargsDict['headers'] = createCSVHeaderList('OSHAAccidentsNAICS4811_4812_4881.csv')

congressCRSKwargsDict = {'csv_file' : 'CRSScrape2.csv',
'uniqueIDColumnName' : 'Bill number',
'newColumnName' : 'CRS Summary',
'csv_file_destination' : '114th Legislation with CRS Summaries2.csv',
'startQuote' : '</span></h3>',
'endQuote' : '</p></div>',
'specialURLs' : 'Congress CRS',
'alternateEndQuoteList' : ['</div>']}

#!/usr/bin/env python
"""
File name: apartmentMasterSearch.py
Author: Matt Thimsen
Date Created: 6/3/2018
Python Version: 3.6.4
Selenium Version: 3.11.0
"""
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor as Executor
from operator import itemgetter


#setup options so that we can run firefox headless
options = Options()
options.set_headless(headless=True)

#get city and state inputs from the user
city=input("\nPlease type the name of the city in lowercase and press enter:\n")
state=input("\nPlease type the initials of the state and press enter:\n")

#----------BUILD NEEDED URLS----------------------------------------------------------------------------------------------------------#

#dict to convert abbreviations to spelled out states (needed for some urls)	
spelledStates = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New-Hampshire',
    'NJ': 'New-Jersey',
    'NM': 'New-Mexico',
    'NY': 'New-York',
    'NC': 'North-Carolina',
    'ND': 'North-Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode-Island',
    'SC': 'South-Carolina',
    'SD': 'South-Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West-Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming',
}

#produce a spelled out state (needed for apartmentFinder.com)
spelledState=spelledStates[state.upper()]
	
#for each website, build the link, low to high (if it can be done)
ApDotCom="https://www.apartments.com/" + city + "-" + state + "/?so=2"
zillow = "https://www.zillow.com/homes/for_rent/" + city + "-" + state + "/condo,apartment_duplex_type/paymenta_sort/"
trulia='https://www.trulia.com/for_rent/' + city +',' + state + '/price;a_sort/'
apartmentFinder = "https://www.apartmentfinder.com/" + spelledState + "/" + city + "-Apartments"


#----------APARTMENTS.COM DATA COLLECTION---------------------------------------------------------------------------------------------#

def ApDotComGet():
	
	#predefine a results list
	ApDotComResults=[]
	
	
	#start a webdriver specific for apartments.com
	driver1=webdriver.Firefox(firefox_options=options)
	
	#go to apartments.com
	driver1.get(ApDotCom)

	#this loop selects each 'placard' (area of html with apartment info) and extracts the info from it,
	for x in range(1,26):
		
		#use while true to set a break point if a caption doesn't have the data we need
		while True:
			placard=driver1.find_element_by_xpath("/html/body/div[1]/main/section/div[1]/section[2]/div[2]/ul/li[" + str(x) + "]/article")
			link=placard.get_attribute('data-url')
			location=placard.find_element_by_class_name('location').text
			
			#try to get price, sometimes it's not listed, so if it isn't don't bother
			try:
				price=placard.find_element_by_class_name('altRentDisplay').text
		
			except selenium.common.exceptions.NoSuchElementException:
				break
			
			#get the availibility
			availability=placard.find_element_by_class_name('availabilityDisplay').text
	
			#check to make sure it's availibe (not always the case on apartments.com)
			if availability is not "Not Available":
				#add data to results
				ApDotComResults.append({"Price":price,"Location":location,"Link":link})
			
			break
	
	
	#shutdown the driver and return results
	driver1.close()
	return ApDotComResults
	
	
	
#----------ZILLOW DATA COLLECTION-----------------------------------------------------------------------------------------------------#


def zillowGet():

	#predefine a results list
	zillowResults=[]
	
	#start a webdriver specific for zillow and go there 
	driver2=webdriver.Firefox(firefox_options=options)
	driver2.get(zillow)
	
	cards=driver2.find_elements_by_xpath("//*[starts-with(@class, 'zsg-photo-card-content ')]")
	
	for card in cards:
		
		#use while true to set a break point if a caption doesn't have the data we need
		while True:
			link=card.find_element_by_xpath(".//*[starts-with(@class, 'zsg-photo-card-overlay-link ')]").get_attribute("href")
	
			location=card.find_element_by_class_name("zsg-photo-card-address").text
		
			#try to get price, sometimes it's not listed, so if it isn't don't bother
			try:
				price=card.find_element_by_class_name("zsg-photo-card-price").text
		
			except selenium.common.exceptions.NoSuchElementException:
				break
		
			#add data to results
			zillowResults.append({"Price":price,"Location":location,"Link":link})
		
			break

	#shutdown the driver and return results
	driver2.close()
	return zillowResults
	
	
#----------TRULIA DATA COLLECTION-------------------------------------------------------------------------------------------------------#

def truliaGet():

	#predefine a results list and counter
	truliaResults=[]
	count=0
	
	#start a webdriver specific for trulia and go there
	driver3=webdriver.Firefox(firefox_options=options)
	driver3.get(trulia)
	
	#while true needed to stop trying in case there is no data in one of these elements, or a paige reload occurs (common with trulia.com)
	while True:
		
		cards=driver3.find_elements_by_xpath("//*[starts-with(@class, 'xsCol12Landscape')]")
		#print(cards)
		
		for card in cards[count:]:
			count=count+1
			
			try:
				link=card.find_element_by_class_name('tileLink').get_attribute('href')
				price=card.find_element_by_xpath(".//*[starts-with(@class, 'cardPrice')]").text
				location=card.find_element_by_xpath(".//*[starts-with(@class, 'h6 typeWeightNormal')]").text
			
				#add data to results
				truliaResults.append({"Price":price,"Location":location,"Link":link})
			
			#if we cannot extract data, don't bother	
			except selenium.common.exceptions.NoSuchElementException as Exception:
				print(Exception)
				pass
		
			#trulia likes to reload leading to stale elements, so just retry
			except selenium.common.exceptions.StaleElementReferenceException as Exception:
				print(Exception)
				break
				
		#if we've gone through everything, end the while loop
		if count>=len(cards):
			break
			
			
	#shutdown driver and return results
	driver3.close()
	return truliaResults
	
	

#----------APARTMENTFINDER DATA COLLECTION-----------------------------------------------------------------------------------------------#

def apartmentFinderGet():
	#predefine a results list
	apartmentFinderResults=[]

	#start a webdriver specific for apartmentFinder and go there
	driver4=webdriver.Firefox(firefox_options=options)
	driver4.get(apartmentFinder)


	#select each type of listing container and combine them into a cumulative list
	level3s=driver4.find_elements_by_xpath("//*[starts-with(@class, 'level3 row a')]")
	level1s=driver4.find_elements_by_xpath("//*[starts-with(@class, 'level1 row a')]")
	listings=level3s+level1s
	
	for listing in listings:
		location=listing.find_element_by_xpath('.//*[@itemprop="address"]').get_attribute('title')
		price=listing.find_element_by_xpath('.//*[@class="altRentDisplay"]').text
		link=listing.find_element_by_xpath('.//*[@class="ellipses"]').get_attribute('href')
	
		if price is not "No Availibility":
			
			#add data tp results
			apartmentFinderResults.append({"Price":price,"Location":location,"Link":link})
	
	#shutdown driver and return results
	driver4.close()
	return apartmentFinderResults
		

#----------MULTIPROCESS EVERYTHING-------------------------------------------------------------------------------------------------------#


t = time.time()

#maybe test pool method too
#https://stackoverflow.com/questions/37873501/get-return-value-for-multi-processing-functions-in-python

#here we use ProcessPoolExecutor because we need to retieve the results of our variables, standard multiproccessing cannot do this
with Executor() as executor:

	#schedule these processes to occur at the same time
	p1=executor.submit(ApDotComGet)
	p2=executor.submit(zillowGet)
	p3=executor.submit(truliaGet)
	p4=executor.submit(apartmentFinderGet)
	
	#retrieve the results
	ApDotComResults=p1.result()
	zillowResults=p2.result()
	truliaResults=p3.result()
	apartmentFinderResults=p4.result()
	
	#combine results into a cumulative list to be ordered later
	results=ApDotComResults+zillowResults+truliaResults+apartmentFinderResults
	
	

#----------BUILD AND PRINT RESULTS--------------------------------------------------------------------------------------------------------#

#predefine a list for results high to low
sortedResults=[]

#this function takes a price in string form and returns an int which is used to order stuff high to low (takes in a string, returns an int)
def truePrice( price ):
	
	#use this string to hold the real price
	priceString=''
	#predifine a timeout
	timeout=0
	
	for char in price:
		#if we find 3 nondigits, we're done
		#this means $750 - $775 will return 750
		if timeout==3:
			return int(priceString)
		
		#if it's a digit append to priceString
		if char.isdigit()==True:
			priceString = priceString + char
		
		else:
			timeout=timeout+1
			
	#return the price as an int
	return int(priceString)
		
	
#add the "true price" to each dict
for result in results:
	result['True Price']=truePrice(result['Price'])

#sort the list by that "true price"
sortedResults=sorted(results, key=itemgetter('True Price'))


print("\n----------------------------------RESULTS-------------------------------------------------------------------------------\n")
print("Price		Location		Link\n")

for result in sortedResults:
	print('{0: <13}'.format(result["Price"])+'\t'+'{0: <65}'.format(result["Location"])+'\t'+result["Link"])

print("\nFinished in : ",time.time()-t)

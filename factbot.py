from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import urllib
import math
import re
import string
import datetime
from getpass import getpass
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
import winsound

def search_wikipedia(search_term,driver):
	driver.get("https://en.wikipedia.org/wiki/"+search_term)
	print("Opened Wikipedia, searched for "+search_term+".")
	
def rankwords(bigstring):

	w = []
	b = bigstring.lower().split(" ")
	
	while b != []:
		w.append([b[0],b.count(b[0])])
		ww = b[0]
		while ww in b:
			b.remove(ww)
			
	w.sort(key=lambda a: a[1])
	return w
	
def eliminate_numerical(lst):

	working_list = lst
	
	for each_element in working_list:
		working_word = each_element[0]
		for i in range(0,len(working_word)):
			if working_word[i].isnumeric():
				each_element[1] = 0

	return working_list
	
def eliminate_shared(l1,l2):

	list1 = l1
	list2 = l2
	flat_list = []
	
	for i in list2:
		for j in i:
			flat_list.append(j)
			
	count_of_eliminated = 0
	
	error = 1
	while error == 1:
		error = 0
		for k in list1:
			if k[0] in flat_list:
				list1.remove(k)
				count_of_eliminated += 1
				error = 1
				
	print("Removed "+str(count_of_eliminated)+" common words from resultant word banks.")

	return list1
	
def open_google():

	chrome_options = webdriver.ChromeOptions()
	prefs = {"profile.default_content_setting_values.notifications" : 2}
	chrome_options.add_experimental_option("prefs",prefs)
	driver = webdriver.Chrome(chrome_options=chrome_options)
	driver.implicitly_wait(10)
	return driver
	
def greeting():
	print("\n\n\nHi! I'm your Quick Research Bot, or QRB for short.")
	
def help_menu():
	print("\nMy function is to search for things on wikipedia and report back with a list of the sentences my algorithms told me were the most relevant to your keywords.")
	print("\nHere is what you can do with me:")
	print("\n\tWrite -s to search for something.")
	print("\tWrite -q to call it a day.")
	print("\tWrite -h to get this menu again.")	
	
#new to github, testing changes	

def menu(n = 0):
	if n == 1:
		help_menu()
	elif n == 2:
		print("\n\t...\n\nI hope that was what you were looking for.")
		return input("\n\tNow what would you like to do? ").strip()[:2]
	elif n == 3:
		print("\nI'm not quite sure what you're asking me to do. Let me explain again what I do.")
		help_menu()
		return input("\n\tWhat would you like to do? (-s, -q, or -h) ").strip()[:2]
	return input("\n\tWhat would you like to do? ").strip()[:2]
	
def goodbye():
	print("\nI hope to do research with you again soon!")
	
def do_searchbot():
	
	search_term = input("\nWhat would you like to get facts about today? ")
	
	driver = open_google()

	search_wikipedia(search_term,driver)
	
	paragraph_web_elements = driver.find_elements_by_tag_name("p")
	
	list_of_ranked_sentences = []
	strings_accumulated = ""

	for each_element in paragraph_web_elements:
		this_element_text = each_element.text
		
		if len(this_element_text) > 25 and not this_element_text.endswith(":"):
			strings_accumulated = strings_accumulated + this_element_text
			list_of_ranked_sentences.append([this_element_text,-3])
			
		#print("Just appended "+this_element_text+" to list of ranked sentences")
		
	list_of_headings = driver.find_elements_by_tag_name('h1')
	list_of_heading2s = driver.find_elements_by_tag_name('h2')
	list_of_heading3s = driver.find_elements_by_tag_name('h3')

	headings_list = []

	for each_heading in list_of_headings:
		headings_list.append(each_heading.text.lower())		
	for each_heading in list_of_heading2s:
		headings_list.append(each_heading.text.lower())		
	for each_heading in list_of_heading3s:
		headings_list.append(each_heading.text.lower())	
		
	#print("THESE ARE HEADINGS: ")
	#print(headings_list)
		
	ranked_word_list1 = rankwords(strings_accumulated)

	strings_accumulated = ""

	for i in range(0,5):

		#look at 5 wikipedia articles to get a bunch of random, commonly used words
		random_article_link = driver.find_element_by_css_selector('#n-randompage > a')
		random_article_link.click()

		paragraph_web_elements = driver.find_elements_by_tag_name("p")

		for each_element in paragraph_web_elements:
			strings_accumulated = strings_accumulated + each_element.text
		
	#rank the words from the 5 pages we found:: IS THIS NECESSARY?	
	ranked_word_list2 = rankwords(strings_accumulated)
	ranked_word_list3 = eliminate_shared(ranked_word_list1,ranked_word_list2)
	ranked_word_list3 = eliminate_numerical(ranked_word_list3)

	for sentence in list_of_ranked_sentences:
		for word_ranking in ranked_word_list3:
			heading_bias = 20
			if word_ranking[0] in sentence[0].split(" "):
				sentence[1] += (word_ranking[1]^2)*word_ranking[0].isalnum()
				if word_ranking[0] in headings_list:
					sentence[1] += heading_bias
					heading_bias /= 4
					#print("Awarded 10 points to "+word_ranking[0]+" for being a word found in headers.")
		sentence[1] = round(sentence[1]/(len(sentence[0])**.5),3)
				
	list_of_ranked_sentences.sort(key=lambda a: a[1])
		
	print('\n')

	for i in range(1,min(len(list_of_ranked_sentences),10)):	
		this_ranked_sentence = list_of_ranked_sentences[-i]
		print("#"+str(i)+". "+getfirstsentence(this_ranked_sentence[0])+"(score "+str(this_ranked_sentence[1])+")\n")
		#print(1000*int(this_ranked_sentence[-1]))
		#winsound.Beep(1000*int(this_ranked_sentence[-1]),100)

	driver.quit()
	
def clean(string):
	
	cleanstring = string
	cleanstring = re.sub('[A-Z]{1}?<=\.', '', cleanstring) #remove periods after capital letters
	cleanstring = re.sub('\.?=[A-Z]', '', cleanstring) #remove periods before capital letters
	cleanstring = re.sub('\[\d+\]', '', cleanstring)
	cleanstring = re.sub("\s?[\(\[].*?[\)\]]","",string)
	cleanstring = re.sub("\s?[\(\[].*?[\)\]]","",string)
	cleanstring.replace(" .",".")
	cleanstring.replace(" ,",".")
	cleanstring = re.sub("\)","",cleanstring)

	return cleanstring
	
def getfirstsentence(bigtext):
	bigtext = clean(bigtext)
	#bigtext = re.sub('\.\s+.?\w+.*','.',bigtext)
	#bigtext = re.sub('\w{1,}?<=\.\s.+','.',bigtext)
	bigtext = re.sub("(?<=\w{3})\.\s{1}.*",".",bigtext)
	return bigtext
	
def main_program():
	greeting()
	user_response = menu(1)
	while user_response != '-q':
		if user_response == '-s':
			do_searchbot()
			user_response = menu(2)
		elif user_response == '-h':
			user_response = menu(1)
		else:
			user_response = menu(3)
	goodbye()

main_program()
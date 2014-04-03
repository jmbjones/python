'''
Alter

A program that will assign a level of uniqueness to a Search_Term class instance and then alter by broadening or narrowing the term as determined by the level of uniqueness

Morgan Jones
Last Updated: 7/28/2011 by Morgan Jones
'''

import string, cPickle
from sanitize import *
from itertools import *
from config import Config

def get_config(file_name):
	'''
	This brings in the information stored in the configuration files and then it is distributed as needed
	Input: name of the configuration file
	Output: variables that are needed to run the program: number of words that makes a term too broad, number of words that makes a term too narrow, number of words that makes a term just right, number of characters in too broad that necessitates an alteration
	'''
	#Opens the file and gets the configuration variables
	f = file(file_name)
	cfg = Config(f)
	#Changes the variables into formats that can be used
	#A search term that has this many words or fewer is considered too broad
	too_broad_cutoff = int(cfg.too_broad_cutoff)
	#A search term that has either number of words below is considered just right
	just_right_cutoffs = cfg.just_right_cutoff.split(',')
	#A search term that has this or more words is considered too narrow
	too_narrow_cutoff = int(cfg.too_narrow_cutoff)
	#If a too broad term has this many characters or fewer then the front % is taken off and a space is put after the end %
	num_char_cutoff = int(cfg.num_characters_cutoff)

	return too_broad_cutoff, just_right_cutoffs, too_narrow_cutoff, num_char_cutoff

def get_nodes(file_name):
	'''
	This gets the nodes that were created in sanitize.py and pickled
	Input: pickled file
	Output: 
	'''
	#Opens the file
	file = open(file_name, 'rb')
	#Unpickles the file
	nodes = cPickle.load(file)

	return nodes

def import_exceptions(file_exceptions):
	'''
	This opens a file of known exceptions to the sanitization process that can be updated by the user and creates a dictionary with the key as the exception as it would appear after sanitization and the value as what it should be replaced with
	Input: text file of user entered exceptions
	Output: dictionary containing those exceptions
	'''
	#Opens the file that holds all the exceptions
	exceptions = open(file_exceptions)
	#Creates a dictionary of the exceptions: key = how search term would appear, value = what it should be shortened to
	exceptions_dict = {}
	for line in exceptions.readlines():
		#New lines are stripped
		line = line.strip('\n')
		#The lines are split at the comma
		line = line.split(',')
		exceptions_dict[line[0].strip('"')] = line[1].strip('"')
	#Closes the file
	exceptions.close()

	return exceptions_dict

def find_exceptions(search_term):
	'''
	This check to see if a search term is an exception. If it is then the name that will be used to search with is the value of the dictionary entry for that exception
	Input: Search_Term class instance
	Output: if needed an updated Search_Terms class instance variable final_name
	'''
	#Creates exceptions dictionary
	exceptions_dict = import_exceptions('exceptions.txt')
	#Checks to see if the search term is an exception
	for key in exceptions_dict:
		if key == search_term.original_name:
			#If it is an exception the name that will be used to search in sql is the exception dictionary key
			search_term.final_name = exceptions_dict[key]
			#Shows that this final name is an exception and therefore will not be changed again
			search_term.exception = True

	return search_term

def multi_split(string, seperators):
	'''
	Splits a string based on a number of different separators
	Input: the string to be split, the different separators it should be split on
	Output: a list of the original string, split on the correct separators
	'''
	#Makes a list of the string
	list_str = [string]
	#For each separator it splits the string
	for sep in seperators:
		string, list_str = list_str, []
		for item in string:
			list_str += item.split(sep)

	return list_str

def assign_level(search_term, too_broad_cutoff, just_right_cutoffs, too_narrow_cutoff, semi_generics):
	'''
	Assigns a level off too narrow, too broad or just right to a search term depending on the number of unique terms in the sanitized name
	Input: Search_Term class instance
	Output: updated Search_Term class instance
	'''
	#Get the current search term, splits it appropriately to find the number of unique terms in the search term
	name = search_term.sanitized_name
	#Split the search term into a list using spaces and percent signs
	name_list = multi_split(name, [' ', '%'])
	#Take out empty items in the list
	name_list = [item for item in name_list if item != '']
	to_remove = []
	for item in name_list:
		if item+'%' in semi_generics.values():
			to_remove.append(item)
	for item in to_remove:
		name_list.remove(item)
	#Find how many unique terms there are in the search term
	num_unique = len(name_list)
	#Assigns a level of uniqueness to the search_term by updating the class variable level
	if num_unique == 0:
		#This joins the search term using the %
		search_term.sanitized_name = '%'.join(search_term.sanitized_terms)
		search_term.sanitized_name = '%'+search_term.sanitized_name+'%'
		#This then splits the search term based on spaces and %
		name_list = multi_split(search_term.sanitized_name, [' ', '%'])
		#This takes out the empty items in the name list
		name_list = [item for item in name_list if item != '']
		num_unique = len(name_list)
		#With the new number of unique items the levels of uniqueness is checked again
		if num_unique == too_broad_cutoff:
			search_term.level = ['too broad', int(num_unique), name_list]
		if num_unique == just_right_cutoffs[0] or num_unique== just_right_cutoffs[1]:
			search_term.level = ['just right', int(num_unique), name_list]
		if num_unique >= too_narrow_cutoff:
			search_term.level = ['too narrow', int(num_unique), name_list]
	else:
		if num_unique == too_broad_cutoff:
			search_term.level = ['too broad', int(num_unique), name_list]
		if num_unique == int(just_right_cutoffs[0]) or num_unique== int(just_right_cutoffs[1]):
			search_term.level = ['just right', int(num_unique), name_list]
		if num_unique >= too_narrow_cutoff:
			search_term.level = ['too narrow', int(num_unique), name_list]

	return search_term

def just_right(search_term):
	'''
	If the search term level is just right (aka 2 unique words) then replace spaces with % and that is the name that will be used to search
	Input: Search_Term class instance
	Output: updated Search_Term class instance
	'''
	#Replaces spaces with %
	search_term.final_name = search_term.sanitized_name.replace(' ', '%')

	return search_term

def too_broad(search_term, num_char_cutoff, semi_generics):
	'''
	If the search term level is too broad(aka 1 unique word) then remove the left % and that is the name that will be used to search
	Input: Search_Term class instance
	Output: updated Search_Term class instance
	'''
	to_remove = []
	name_list = multi_split(search_term.sanitized_name, [' ', '%'])
	for item in name_list:
		if item+'%' in semi_generics.values():
			to_remove.append(item)
	for item in to_remove:
		name_list.remove(item)
	new_name = '%'.join(name_list)
	if len(name_list[0])-2 <= num_char_cutoff:
		#Take off the front %
		search_term.final_name = new_name.lstrip('%')
		#Take off the end %
		search_term.final_name = search_term.final_name.rstrip('%')
		#Put back on % with a space in front of it
		search_term.final_name = search_term.final_name+' %'
		for item in to_remove:
			search_term.final_name = search_term.final_name+item+'%'
	else:
		#Otherwise leave the search term alone
		search_term.final_name = search_term.sanitized_name
	
	return search_term

def combos(search_term):
	'''
	This creates all of the possible combinations of the search term when one word is removed
	Input: search_term
	Output: tuple of tuples of combinations of size n-1 terms in the search term
	'''
	#Gets the number of unique terms in the search term from the class variable level
	num_unique = int(search_term.level[1])
	#Gets the search term as a list from the class variable level
	name_list = search_term.level[2]
	#Creates a tuple of tuples of the different possible combinations of size n-1 of terms in the search term
	possibilites = combinations(name_list, num_unique-1)

	return possibilites

def gain_characters(possibilites):
	'''
	Finds the search term that will yield the most information gain based on the number of characters
	Input: tuple of tuples of all possible combinations of size n-1 of the search term words
	Output: a search term
	'''
	#Checks the number of characters of the search terms
	longest  = ' '
	for item in possibilites:
		#The longest is kept and updated when a longer one is checked
		if len(' '.join(item)) > len(longest):
			longest = '%'.join(item)

	return longest

def too_narrow(search_term):
	'''
	This checks all of the possible combinations of the search term when one word is removed. The longest of these (most characters) is chosen as the name that will be used to search
	Input: Search_Term class instance
	Output: updated Search_Term class instance
	'''
	#Creates all possible n-1 combinations of search term words
	possibilites = combos(search_term)
	#Finds the best n-1 search term (based on number of characters
	best = gain_characters(possibilites)
	#Adds back in the % on the front and end
	best = '%'+best+'%'
	#Makes the final search term the n-1 size search term with the most characters
	search_term.final_name = best
	#Updates the level as well
	search_term.level[1] = search_term.level[1]-1
	search_term.level[2] = multi_split(best, [' ', '%'])

	return search_term

def alter_name(search_term, num_char_cutoff, semi_generics):
	'''
	Checks the level of uniqueness and changes the search term as necessary
	Input: Search_Term class instance
	Output: Search_Term class instance
	'''
	#Checks to see if the search term is an exception
	if search_term.exception == True:
		#If it an exception return the node as is
		return search_term
	else:
		#Otherwise check the level and alter the search term appropriately
		if search_term.level[0] == 'too broad':
			search_term = too_broad(search_term, num_char_cutoff, semi_generics)
		elif search_term.level[0] == 'just right':
			search_term = just_right(search_term)
		else:
			search_term = too_narrow(search_term)

		return search_term

def finish_up():
	too_broad_cutoff, just_right_cutoffs, too_narrow_cutoff, num_char_cutoff = get_config('config_alter.txt')
	#This reads in the Search_Term class instances created and updated by sanitize.py
	nodes = get_nodes('sanitized_nodes')
	#For each of the nodes in the nodes list they are categorized and altered to improve recall
	final_names = []
	search_terms = []
	original_names = []
	#Creates the list of generic terms and dictionary of semi-generic terms
	generic_terms, semi_generics = generic_files('generic_terms.txt', 'semi_generic_terms.txt')
	for search_term in nodes:
		#These change the search_terms appropriately and update the class instance
		search_term = find_exceptions(search_term)
		search_term = assign_level(search_term, too_broad_cutoff, just_right_cutoffs, too_narrow_cutoff, semi_generics)
		search_term = alter_name(search_term, num_char_cutoff, semi_generics)
		#This replaces all non-ascii characters in the original company name from the customer with a ?
		for char in search_term.original_name:
			if char not in string.printable:
				search_term.original_name = search_term.original_name.replace(char, '?')
		#Add the appropriate parts of the node to their respective lists
		original_names.append(search_term.original_name)
		final_names.append(search_term.final_name)
		search_terms.append(search_term)
		print search_term.sanitized_name
	#The Search_Term class instances that have been created are pickled into a format that can be opened by narrow.py
	cPickle.dump(search_terms, open('done_nodes', 'wb'))

	return original_names, final_names, search_terms

def main():
	original_names, final_names, search_terms = finish_up()

if __name__ == '__main__':
	main()
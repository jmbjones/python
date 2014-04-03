'''
This program will classify the test set of numbers using a Naive Bayes Algorithm. Using the probability that a car will be bought or not and all the relative probabilities of the attributes, an instance can be classified as a yes or no to buying.
'''

'''
Reorganize the data so that it can be used in subsequent functions. It is first split and all intances are created as lists and then put into a larger list called newData. Then it counts the number of labels associated with yes and no. Creates dictionaries of counts of all the labels for each index for both yes and no in seperate lists of dictionaries.
'''

from decimal import *
from random import *

def orderData(file):
	fileName = open(file)
	newData = []
	#newData is created here
	for line in fileName:
		line = line.split(',')
		#line = line.strip('\n')
		lineList = []
		for item in line:
			lineList.append(item)	
		newData.append(lineList)
	
	#The test and training sets are created here
	seed(1)
	
	testSet = sample(newData, 173)
	
	trainingSet = []
	for item in newData:
		if item not in testSet:
			trainingSet.append(item)
	
	#Here the training set is split up classification to make counting the number times a label appears in each easier.
	yesData = []
	noData = []
	for item in trainingSet:
		if (item[6] == 'vgood\n' or item[6] == 'good\n' or item[6] == 'acc\n'):
			yesData.append(item)
		if item[6] == 'unacc\n':
			noData.append(item)
	
	#Here dictionaries are created and the label is stored as a keyword and the count of the number of times the label appears for the classification yes or no as the data.
	yesDictionaries = []
	noDictionaries = []
	index = 0
	while index <= 6:
		dictYes = {}
		dictNo = {}
		yesDictionaries.append(dictYes)
		noDictionaries.append(dictNo)
		index += 1
	
	for item in yesData:
		labelIndex = 0
		for i in item:
			indexDictionary = yesDictionaries[labelIndex]
			if i in indexDictionary:
				counter = indexDictionary.get(i)
				counter += 1
				indexDictionary[i] = counter
			else:
				indexDictionary[i] = 1
			labelIndex += 1
		
	for item in noData:
		labelIndex = 0
		for i in item:
			indexDictionary = noDictionaries[labelIndex]
			if i in indexDictionary:
				counter = indexDictionary.get(i)
				counter += 1
				indexDictionary[i] = counter
			else:
				indexDictionary[i] = 1
			labelIndex += 1	
	
	return newData, testSet, trainingSet, yesDictionaries, noDictionaries, yesData, noData
	
'''
Classify each instance as to wether or not to buy the car, yes or no, using the probabilities calculated using the dictionaries created in orderData
'''
def classify(instance):
	newData, testSet, trainingSet, yesDictionaries, noDictionaries, yesData, noData = orderData('car.data')
	
	yesProbabilites = []
	noProbabilites = []
	labelIndex = 0
	
	#This calculates the probabilty that a label will appear with a classification yes. 
	for item in instance:
		yesDictionary = yesDictionaries[labelIndex]
		if yesDictionary.get(item) == None:
			probYes = 0
		else:
			countYes = yesDictionary[item]
			getcontext().prec = 16
			probYes = Decimal(countYes)/Decimal(len(newData))
			yesProbabilites.append(probYes)
		labelIndex += 1
	
	#This calculates the probability that a label will appear with a classification no.
	labelIndex = 0
	for item in instance:
		if (item == 'vgood\n' or item == 'good\n' or item == 'acc\n'):
			pass
		else:
			noDictionary = noDictionaries[labelIndex]
			countNo = noDictionary[item]
			getcontext().prec = 16
			probNo = Decimal(countNo)/Decimal(len(newData))
			noProbabilites.append(probNo)
			labelIndex += 1

#This calculates the total probability of an instance for both yes and no. The numerator of the Bayes formula.	
	totalYes = len(yesData)
	totalNo = len(noData)
	getcontext().prec = 16
	
	pTotalYes = Decimal(totalYes)/Decimal(1728)
	pTotalNo = Decimal(totalNo)/Decimal(1728)
	pYes = 1
	for item in yesProbabilites:
		pYes *= item
	pYes *= pTotalYes
	
	pNo = 1
	for item in noProbabilites:
		pNo *= item
	pNo *= pTotalNo

#This compares the probabilities for each calculation and then determines a classification based on those.	
	if pYes > pNo:
		classification = 'Yes'
	else: 
		classification = 'No'
	return classification

'''
This main will classify all of the items in the test set and then calculate the accuracy by comparing the predicted classification with the actual classification
'''
if __name__ == '__main__':
	newData, testSet, trainingSet, yesDictionaries, noDictionaries, yesData, noData = orderData('car.data')

	rightPrediction = 0
	for item in trainingSet:
		predictedClassification = classify(item)
		if (item[6] == 'acc\n' or item[6] == 'good\n' or item[6] == 'vgood\n'):
			actualClassification = 'Yes'
		else:
			actualClassification = 'No'
		if predictedClassification == actualClassification:
			rightPrediction += 1
	getcontext().prec = 16
	accuracy = Decimal(rightPrediction)/Decimal(len(trainingSet))
	print accuracy
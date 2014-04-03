'''
Agglomerative Clustering Program
By Morgan Jones
'''

from math import *
from heapq import *

def logTransform(fileName, numLines):
	#This logs all the points and puts them into lists
	data = open(fileName)
	
	clusters = []
	for line in data:
		singleCluster = []
		lineTemp = line.replace(' ', '')
		tempLine = lineTemp.split()
		logLine = []
		for item in tempLine:
			numberItem = float(item)
			logItem = log((numberItem+1), 2)
			logLine.append(logItem)
		singleCluster.append(logLine)
		clusters.append(singleCluster)
		
	return clusters[:numLines]
	
def normalizeData(fileName, numLines):
	#This normalizes all the rows and puts them into lists
	data = open(fileName)
	
	clusters = []
	for line in data:
		singleCluster = []
		lineTemp = line.replace(' ', '')
		tempLine = lineTemp.split()
		normLine = []
		for item in tempLine:
			numberItem = float(item)
			sqItem = numberItem**2
			normLine.append(sqItem)
		normTotal = sum(normLine)
		normTotalSqrt = sqrt(normTotal)
		normedLine = []
		for item in tempLine:
			numberItem = float(item)
			newItem = numberItem/normTotalSqrt
			normedLine.append(newItem)
		singleCluster.append(normedLine)
		clusters.append(singleCluster)
		
	return clusters[:numLines]

def euclideanSqDist(center1, center2):
	#This calculates Euclidean Square Distance between two points
	differences = []
	index = 0
	for item in center1:
		difference = item - center2[index]
		diffSq = difference**2
		differences.append(difference)
		index += 1
	distance = abs(sum(differences))
	
	return distance

def recalculateCenter(cluster1Index, cluster2Index, clusters):
	#This recalculates the center for a new cluster
	cluster1 = clusters[cluster1Index]
	cluster2 = clusters[cluster2Index]
	
	index = 0
	total = 0
	totals = []
	item = cluster1[0]
	for i in item:
		totals.append(0)
	
	if len(cluster1) > len(cluster2):
		indexPoint = 0
		for item in cluster1:
			indexItem = 0
			for i in item:
				try:
					i2 = cluster2[indexPoint][indexItem]
				except IndexError:
					i2 = 0
				totals[indexItem] = i + i2 + totals[indexItem]
				indexItem += 1
			indexPoint += 1
	else:
		indexPoint = 0
		for item in cluster2:
			indexItem = 0
			for i in item:
				try:
					i2 = cluster1[indexPoint][indexItem]
				except IndexError:
					i2 = 0
				totals[indexItem] = i + i2 + totals[indexItem]
				indexItem += 1
			indexPoint += 1

	cluster1.extend(cluster2)
	newCluster = cluster1
	clusters.insert(cluster1Index, newCluster)
	clusters.remove(cluster2)
	clusters.remove(cluster1)
	#Index of the new center is the same as Cluster 1 because the new cluster is being put where cluster 1 used to be and therefore the corresponding center needs to be at the same index in the center List
	centerIndex = cluster1Index
	
	newCenter = []
	for item in totals:
		numberClusters = len(cluster1[0])
		meanItem = float(item)/float(numberClusters)
		newCenter.append(meanItem)
		
	return newCenter, centerIndex, clusters
	
def createHeap(centerList):
	#Create list of distances in tuple with centers
	distanceIndex = 0
	allDist = []
	#Create a list of pairs of items
	pairs = []
	pairs = [(x,y) for x in centerList for y in centerList]
	for item in pairs:
		if item[0] == item[1]:
			pairs.remove(item)
	for item in pairs:
		for otherItem in pairs:
			if item[0] == otherItem[1] and item[1] == otherItem[0]:
				pairs.remove(otherItem)
	for item in pairs:
		allDist.append((euclideanSqDist(item[0], item[1]), item))

	#Create the heap with the tuples, using a min heap and having the first item be the distance so it will be sorted by distance	
	heapDist = []
	for item in allDist:
		heappush(heapDist, item)
	
	return heapDist
	
def updateCenters(heap, clusters, centerList):
	#This updates the centerList and calls recalculate center so that the cluster and center lists continue to match indexes
	closest = heappop(heap)

	center1 = closest[1][0]
	center2 = closest[1][1]

	cluster1Index = centerList.index(center1)
	cluster2Index = centerList.index(center2)
	
	newCenter, centerIndex, clusters = recalculateCenter(cluster1Index, cluster2Index, clusters)
	
	centerList.remove(center1)
	centerList.remove(center2)
	centerList.insert(centerIndex, newCenter)
	
	return centerList, clusters

def calculateError(clusters, centerList):
	#Distance between each point in cluster and center
	errors = []
	for cluster in clusters:
		center = centerList[clusters.index(cluster)]
		for point in cluster:
			error = euclideanSqDist(point, center)
			errors.append(error)
	TCE = sum(errors)
	return TCE

if __name__ == '__main__':

	#clusters = logTransform('wp_namespace2.data.txt', 100)
	clusters = normalizeData('wp_namespace2.data.txt', 100)
	centerListLists = clusters
	centerList = []
	for item in centerListLists:
		for i in item:
			centerList.append(i)

	distHeap = createHeap(centerList)
	TCE1 = calculateError(clusters, centerList)

	while len(clusters) > 1:
		centerList, clusters = updateCenters(distHeap, clusters, centerList)
		#This is where you lose efficiency because you are creating the heap everytime rather than updating it
		distHeap = createHeap(centerList)
		TCE = calculateError(clusters, centerList)
		if len(clusters) == 5:
			print 'logged', centerList
'''
Laurel Orr and Morgan Jones
Final Project
'''

from itertools import *
from math import *
from random import *

class Node:
    def __init__(self, points, col, att, clss, left, right, level):
        '''
        If node is leaf, test condition column, test condition attributes, left, and right will be None. If node is not leaf, the classification will be None
        '''
        self.points = points
        self.testCol = col
        self.testAttributes = att
        self.classification = clss
        self.left = left
        self.right = right
        self.level = level
        
    def printN(self):
        '''
        Prints the node
        '''
        print 'Level: ', self.level
        printArray(self.points, "Points")
        print "Data: "
        print "Col: ", self.testCol, " Att: ", self.testAttributes, " Class: ", self.classification
        
    def printArray(array, title):
        '''
        Prints an array where each row is on one line with a title.Input: array and string title.
        Output: print array
        '''
        print title
        if len(array) == 0:
            print "(empty)"
        else:
            for item in array:
                print item
        print

def readDataFromFile(fileName):
    '''
    Read the data from the file abd store as a 2D list. Input: file name. Output: list of rows in the data, a header dictionary where keys are headers and values are possible attributes, and the list of headers
    '''
    dataList = []
    headerDict = {}
    file = open(fileName, "r")
    header = file.readline().strip().split("\t")
    for att in header:
        headerDict[att] = []
    for line in file:
        temp = []
        line = line.strip()
        line = line.split("\t")
        dataList += [line]
    file.close()
    length = len(dataList[0])
    for row in dataList:
        for i in range(length):
             if row[i] not in headerDict[header[i]]:
                  headerDict[header[i]].append(row[i])
                  headerDict[header[i]].sort()
    return dataList, headerDict, header
    
def createTestSet(dataSet):
        '''
        Creates the test set and training set. Train set be 85% of the full set (227) and test set be 15% (40)
        '''
        testSet = []
        seed(0) #ensures that I generate the same test and training set each time
        sizeCounter = 0
        while sizeCounter != int(0.1 * len(dataSet)):
            ranNum = randint(0, len(dataSet) - sizeCounter)
            entry = dataSet.pop(ranNum)
            testSet.append(entry)
            sizeCounter += 1
        return dataSet, testSet

def gini(nodeList):
   '''
   Finds the gini impurity using the equation gini = 1 - sum(p(i|t)^2)
   where p(i|t) is the fraction of records belonging to a class i and a given node t. The nodeList is all of the items in node t. We will always be doing binary classifications so the classification will be "1". Input: node t and class i. Output: gini imputity, count of number points will classification. 
   '''
   length = float(len(nodeList))
   sum = 0
   count = 0
   if length != 0:
       for node in nodeList:
           if node[-1] == "Alive":
               count += 1
       sum += (count / length)**2
       sum += ((length - count) / length)**2
       return 1 - sum
   else:
       return 0
   
def entropy(nodeList):
    '''
    Finds the entropy imputity measure using the equation entropy = -sum(p(i|t)log_2(p(i|t))). We will always use binary classifications. Input: nodeList. Output: entropy impurity.
    '''
    length = float(len(nodeList))
    sum = 0
    count = 0
    if length != 0:
        for node in nodeList:
            if node[-1] == "Alive":
                count += 1
        sum += ((count / length) * log((count / length), 2))
        sum += (((length - count) / length) * log(((length - count) / length), 2))
        return -1 * sum
    else:
        return 0

def classError(nodeList):
    '''
    Finds the classification error imputity using the equation impurity = 1 - max(p(i|t)). We will always use binary classifications. Input: nodeList. Output: calssification impurity.
    '''
    length = float(len(nodeList))
    maxValue = 0
    count = 0
    if length != 0:
        for node in nodeList:
            if node[-1] == "Alive":
                count += 1
        maxValue = max(count, 1 - count)
        return 1 - (maxValue / length)
    else:
        return 0

def splitNodeB(nodeList, col, attList):
    '''
    Splits the nodeList into two separate nodes given the attribute(s). If a point's attributes is in the list of attributes, that points goes to the left node. Input: list of points in a node, col number, and list of attributes. Output: left child and right child of that node.
    '''
    left = []
    right = []
    for node in nodeList:
        if node[col] in attList:
            left.append(node)
        else:
            right.append(node)
    return left, right
    
def findBestSplit(node, headerDict, header):
    '''
    For the list of attributes, find the attribute which give the purest split. Input: node, headerDict, header. Output: attribute split, column number, left child points, and right child points
    '''
    pointList = node.points
    finalLeft = []
    finalRight = []
    finalSplit = () #stores a tuple of the column data and the attribute of the best split
    minImpurity = 1
    for col in range(len(pointList[0]) - 1): #-1 for the classification column
        attList = headerDict[header[col]]
        for size in range((len(attList) / 2) + 1):
            atts = combinations(attList, size) #gets attribute combinations to try
            for comb in atts:
                #print "Col: ", col
                left, right = splitNodeB(pointList, col, comb)
                tempL = gini(left)
                tempR = gini(right)
                #finds the weighted sum of the left and right impurity measures
                tempTotal = ((float(len(left)) / (len(pointList))) * tempL)
                tempTotal += ((float(len(right)) / (len(pointList))) * tempR)
                #print "Gini: ", tempIm
                if tempTotal < minImpurity:
                    finalCol = col
                    finalAtt = comb
                    minImpurity = tempTotal
                    finalLeft = left
                    finalRight = right
    return finalCol, finalAtt, finalLeft, finalRight

def stoppingCond(node):
    '''
    Ideal stopping condition is if every point in a node has the same classification. Input: node. Output: true or false
    '''
    pointList = node.points
    #checking if all attributes are the same
    temp = True
    list1 = pointList[0][:-2] #remember the last column is the classification
    for point in pointList[1:]:
        list2 = point[:-2]
        if list1 != list2:
            temp = False
    if temp:
        return True
    #checks to see if all classifications are the same
    clf = pointList[0][-1] #classification of 1st node
    for point in pointList:
        if point[-1] != clf:
            return False
    return True

def buildTreeHlp(pointList, int, headerDict, header):
   '''
   Helper function for our build tree function to make it recursive. Input: nodeList, headerDict, header. Output: node
   '''
   child = Node(pointList, None, None, None, None, None, int)
   print "STOP: ", stoppingCond(child)
   if stoppingCond(child):
       #child is a leaf
       child.classification = findClassification(child)
   else:
       col, att, left, right = findBestSplit(child, headerDict, header)
       #checks if the best split is to repeat previous split which would cause infinite loop
       if len(left) == 0 or len(right) == 0:
           child.classification = findClassification(child)
       else:
           child.testCol = col
           child.testAttributes = att
           child.left = buildTreeHlp(left, int + 1, headerDict, header)
           child.right = buildTreeHlp(right, int + 1, headerDict, header)
   
   return child

def buildTree(nodeList, headerDict, header):
    '''
    Main function that builds our decision tree. Input: list of all initial points, headerDict, header. Output: final split list
    '''
    root = Node(nodeList, None, None, None, None, None, 0)
    print "ROOT"
    root.printN()
    col, att, left, right = findBestSplit(root, headerDict, header)
    root.testCol = col
    root.testAttributes = att
    root.left = buildTreeHlp(left, 1, headerDict, header)
    root.right = buildTreeHlp(right, 1, headerDict, header)
    printTree(root)

def findClassification(leaf):
    pointList = leaf.points
    aliveCount = 0
    for point in pointList:
        if point[-1] == "Alive":
            aliveCount += 1
    if aliveCount == max(aliveCount, len(pointList) - aliveCount):
        return "Alive"
    else:
        return "Dead"

def printArray(array, title):
    '''
    Prints an array where each row is on one line with a title.Input: array and string title.
    Output: print array
    '''
    print title
    if len(array) == 0:
        print "(empty)"
    else:
        for item in array:
            print item
    print
            
def printDict(dict, title):
    '''
    Prints dictionary where each key is a header and the values are on separate lines below.
    Input: dict and string title. Output: print dict
    '''
    print title
    for key in dict.keys():
        print "KEY: ", key
        for item in dict[key]:
             print item
    print
    
def printTree(root):

    if root != None:
        root.printN()
        printTree(root.left)
        printTree(root.right)

def main():
    #fileName = raw_input("Text File Please: ")
    fileName = "titanic.txt"
    dataList, headerDict, header = readDataFromFile(fileName)
    print "HEADER: ", headerDict
    trainSet, testSet = createTestSet(dataList)
    buildTree(testSet, headerDict, header)
    
    
#ATTRIBUTE GOES TO THE LEFT SO IF ATT = 0, THEN LEFT CHILD HAS ATT = 0, RIGHT CHILD HAS ATT NOT 0



if __name__ == '__main__':
    main()
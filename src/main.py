#
#
#  -*- coding: utf-8 -*-
#
#
import requests
import numpy as np
import time
import sys
import csv

from bs4 import BeautifulSoup

# SET NUMPY TRUNCTAION:
np.set_printoptions(threshold=sys.maxsize)


def getURL(userName):
    return 'https://dota2.ru/forum/search/?type=post&keywords=&users=' + userName + '&date=&nodes%5B%5D=all'

def getPageByNumber(URL, num:int):
    page = requests.get(URL + '&page=' + str(num))
    return BeautifulSoup(page.text, 'html.parser')

def countPages(URL, mainNum=1):
    page = getPageByNumber(URL, mainNum)
    pageContainer = str(page.find(class_='page-container-wrap'))
    for i in range(len(pageContainer)):
        subString = pageContainer[i: i+10]
        if subString == 'data-pages':
            return int(pageContainer[i+12: i+15])

def findAllPostLinksOnPage(postsPage):
    z = ["1", "2"]
    res = np.empty(shape=0, dtype=str)
    class_posts = postsPage.find(class_='search-results-list')
    posts = str(class_posts.find_all('a'))
    for i in range(len(posts)):
        subString = posts[i: i+11]
        if subString == 'href="posts':
            res = np.hstack((res, posts[i+6: i+20]))
    return res

def getAllPostsId(URL, lastPageNum:int):
    res = np.empty(shape=0, dtype=object)
    for i in range(1, lastPageNum + 1):
        page = getPageByNumber(URL, i)
        res = np.hstack((res, findAllPostLinksOnPage(page)))
    return res

def getAllPostsURLs(postsId):
    """postsId is numpy array"""
    for i in range(len(postsId)):
        postsId[i] = 'https://dota2.ru/forum/' + postsId[i]
    return postsId

def checkForQuote(postHTML:str):
    for i in range(len(postHTML)):
        if postHTML[i: i+11] == 'data-author':
            return True
    return False

def getStringHTMLPostFromURL(postURL):
    """But till without quotes / emotes / img and etc"""
    postId = postURL[29: len(postURL)]
    page = requests.get(postURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    post = str(soup.find(id='message-container-' + postId).find(class_='messageText baseHtml'))
    return post

def getPostFromHTML(postHTML:str):
    if not checkForQuote(postHTML):
        try:
            start = postHTML.index('<p>')
            stop = postHTML.index('</p>')
            post =  (postHTML[start+3:stop]).lower()
            return ((((((post.replace('\xa0', '')).replace(',', '')).replace('-', '')).replace('.', '')).replace('?', '')).replace(')', '')).replace('(', '')
        except ValueError as e:
            return 'addskypochini<p>iliyadayn'
    return "nullexquote"

def allPostsString(postsURLs):
    """postsURLs - numpy array"""
    allPostsData = np.empty(shape=0, dtype=str)
    for postURL in postsURLs:
        postHTML = getStringHTMLPostFromURL(postURL)
        post = getPostFromHTML(postHTML)
        allPostsData = np.hstack((allPostsData, post))
    return allPostsData

def deleteQuotesFromArray(allPostsData):
    return allPostsData[allPostsData != 'nullexquote']

def countWords(allPostsData):
    wordsData = np.empty(shape=0, dtype=str)
    countWords = np.empty(shape=0, dtype=int)
    for i in range(len(allPostsData)):
        splittedPost = allPostsData[i].split(' ')
        for j in range(len(splittedPost)):
            if splittedPost[j] not in wordsData:
                wordsData = np.hstack((wordsData, splittedPost[j]))
                countWords = np.hstack((countWords, 1))
            else:
                index = np.where(wordsData == splittedPost[j])
                countWords[index] += 1
    return wordsData, countWords

def wordRules(word):
    if  '<img' in word:
        return False
    if 'datasmile=' in word:
        return False
    if 'datashortcut=' in word:
        return False
    if 'alt=' in word:
        return False
    if 'title=' in word:
        return False
    if 'src=' in word:
        return False
    if 'href=' in word:
        return False
    return True



def mostInData(wordsData, countWords):
    data = np.empty(shape=[0, 2])
    for i in range(len(countWords)):
        if wordRules(wordsData[i]):
            data = np.append(data, [[wordsData[i], countWords[i]]], axis=0)
    return data

def writeTXT(data, userName, filename='output.csv'):
    with open(filename, 'w') as f:
        csv.register_dialect("custom", delimiter=",", skipinitialspace=True)
        writer = csv.writer(f, dialect="custom")
        for i in range(-1, len(data)):
            if (i == -1):
                string = ('nickname', userName)
                writer.writerow(string)
                continue
            writeData = (data[i][0], data[i][1])
            writer.writerow(writeData)


def main():
    userName = input("$userName: ")
    pagesLimit = int(input("$pagesLimit: "))
    t1 = time.time()
    URL = getURL(userName)
    a = getAllPostsId(URL, pagesLimit)
    b = getAllPostsURLs(a)
    arr = deleteQuotesFromArray(allPostsString(b))
    wData, cWords = countWords(arr)

    data = mostInData(wData, cWords)

    writeTXT(data, userName)


if __name__ == '__main__':
    main()



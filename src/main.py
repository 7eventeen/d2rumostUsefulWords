import requests
from bs4 import BeautifulSoup
import numpy as np
import time
import re


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
    postId = postURL[29: len(postURL)]
    page = requests.get(postURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    post = str(soup.find(id='message-container-' + postId).find(class_='messageText baseHtml'))
    return post

def checkForQuote(postHTML:str):
    for i in range(len(postHTML)):
        if postHTML[i: i+11] == 'data-author':
            return True
    return False

def getPostFromHTML(postHTML:str):
    """For posts with quotes are so not trivial solution"""
    if not checkForQuote(postHTML):
        start = postHTML.index('<p>')
        stop = postHTML.index('</p>')
        post =  (postHTML[start+3:stop]).lower()
        return ((((post.replace('\xa0', '')).replace(',', '')).replace('-', '')).replace('.', '')).replace('?', '')
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

def mostInData(wordsData, countWords, wordsLimit=45):
    countWordsSorted = -np.sort(-countWords)
    k = 0
    for i in range(len(countWordsSorted)):
        index = np.where(countWords == countWordsSorted[i])
        print(wordsData[index], countWordsSorted[i])
        k += 1
        if k > wordsLimit:
            return


def main(userName='Bonessa97', pagesLimit=50):
    t1 = time.time()
    URL = getURL(userName)
    postsId = getAllPostsId(URL, pagesLimit)
    postsURLs = getAllPostsURLs(postsId)
    arr = deleteQuotesFromArray(allPostsString(postsURLs))
    wData, cWords = countWords(arr)

    mostInData(wData, cWords)

    print(time.time() - t1)

if __name__ == '__main__':
    main()



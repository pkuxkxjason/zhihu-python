# -*- coding: utf-8 -*-


import platform
import re

import requests
from bs4 import BeautifulSoup

import answer
import question
import user


class Collection:
    url = None
    # session = None
    soup = None

    def __init__(self, url, name=None, creator=None):

        #if url[0:len(url) - 8] != "http://www.zhihu.com/collection/":
        if not re.compile(r"(http|https)://www.zhihu.com/collection/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a collection url.")
        else:
            self.url = url
            # print 'collection url',url
            if name != None:
                self.name = name
            if creator != None:
                self.creator = creator
    def parser(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, "lxml")
        self.soup = soup

    def get_name(self):
        if hasattr(self, 'name'):
            if platform.system() == 'Windows':
                return self.name.decode('utf-8').encode('gbk')
            else:
                return self.name
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            self.name = soup.find("h2", id="zh-fav-head-title").string.encode("utf-8").strip()
            if platform.system() == 'Windows':
                return self.name.decode('utf-8').encode('gbk')
            return self.name

    def get_creator(self):
        if hasattr(self, 'creator'):
            return self.creator
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            creator_id = soup.find("h2", class_="zm-list-content-title").a.string.encode("utf-8")
            creator_url = "http://www.zhihu.com" + soup.find("h2", class_="zm-list-content-title").a["href"]
            creator = User(creator_url, creator_id)
            self.creator = creator
            return creator

    def get_all_answers(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        answer_list = soup.find_all("div", class_="zm-item")
        if len(answer_list) == 0:
            print "the collection is empty."
            return
            yield
        else:
            question_url = None
            question_title = None
            for answer in answer_list:
                if not answer.find("p", class_="note"):
                    question_link = answer.find("h2")
                    if question_link != None:
                        question_url = "http://www.zhihu.com" + question_link.a["href"]
                        question_title = question_link.a.string.encode("utf-8")
                    question = Question(question_url, question_title)
                    answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a["href"]
                    author = None

                    if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                        author_url = None
                        author = User(author_url)
                    else:
                        author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
                        author_id = author_tag.string.encode("utf-8")
                        author_url = "http://www.zhihu.com" + author_tag["href"]
                        author = User(author_url, author_id)
                    yield Answer(answer_url, question, author)
            i = 2
            while True:
                r = requests.get(self.url + "?page=" + str(i))
                answer_soup = BeautifulSoup(r.content, "lxml")
                answer_list = answer_soup.find_all("div", class_="zm-item")
                if len(answer_list) == 0:
                    break
                else:
                    for answer in answer_list:
                        if not answer.find("p", class_="note"):
                            question_link = answer.find("h2")
                            if question_link != None:
                                question_url = "http://www.zhihu.com" + question_link.a["href"]
                                question_title = question_link.a.string.encode("utf-8")
                            question = Question(question_url, question_title)
                            answer_url = "http://www.zhihu.com" + answer.find("span", class_="answer-date-link-wrap").a[
                                "href"]
                            author = None
                            if answer.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                                # author_id = "匿名用户"
                                author_url = None
                                author = User(author_url)
                            else:
                                author_tag = answer.find("div", class_="zm-item-answer-author-info").find_all("a")[0]
                                author_id = author_tag.string.encode("utf-8")
                                author_url = "http://www.zhihu.com" + author_tag["href"]
                                author = User(author_url, author_id)
                            yield Answer(answer_url, question, author)
                i = i + 1

    def get_top_i_answers(self, n):
        j = 0
        answers = self.get_all_answers()
        for answer in answers:
            j = j + 1
            if j > n:
                break
            yield answer
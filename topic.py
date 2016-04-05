# -*- coding: utf-8 -*-
import auth
from zhihu import Zhihu, requests
from user import User
import re
import simplejson
import time
import sys

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup


class Topic(Zhihu):
    def __init__(self, url):
        if not re.compile(r"(http|https)://www.zhihu.com/topic/\d{8}").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a topic  url.")
        super(Topic, self).__init__(url)
        self.name = ""
        self.followers = None

    def get_followers(self):
        self.follower_url = self.url + "/followers"
        self.followers = TopicFollowers(self.follower_url)
      

class TopicFollowers(Zhihu):
    def __init__(self, url):
        if not re.compile(r"(http|https)://www.zhihu.com/topic/\d{8}/followers").match(url):
            raise ValueError("\"" + url + "\"" + " : it isn't a topic followers url.")
        super(TopicFollowers, self).__init__(url)
        self.name = ""
        self.followers = []

    def _find_all_user_blocks(self):
        user_list = self.soup.find_all("div", class_="zm-person-item")
        last_user_reg_date = None
        followers = []
        for u in user_list:
            url = "https://www.zhihu.com"+u.find("h2", class_="zm-list-content-title").find("a")["href"]
            last_user_reg_date = u["id"][3:]
            followers.append(User(url))
        return followers, last_user_reg_date 

    def _get_followers_num(self):
        return int(self.soup.find("div",class_="zm-topic-side-followers-info").find("strong").string)

    def get_followers_raw(self):
        if not self.soup:
            self.parse()
        return_followers = []
        followers, last_user_reg_date = self._find_all_user_blocks()
        return_followers += followers

        # pagination
        _xsrf = self.soup.find("input", attrs={'name': '_xsrf'})["value"]
        header = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            'Host': "www.zhihu.com",
            'Referer': self.url,
        }

        followers_num = self._get_followers_num()
        print "#followers:", followers_num

        for page_num in range(1, (followers_num - 40) / 20):
            print '\n*',
            sys.stdout.flush()
            time.sleep(0.1)
            data = {"offset": 20 + page_num * 20, "start": last_user_reg_date, "_xsrf": _xsrf}
            try:
                r = requests.post(self.url, data=data, headers=header)
                response = simplejson.loads(r.content)
                html_body = BeautifulSoup(response["msg"][1].encode("utf-8"), "lxml")
                followers, last_user_reg_date = self._find_all_user_blocks(html_body)
                return_followers += followers
            except Exception, e:
                continue

        return return_followers

    def get_followers(self):
        if not self.soup:
            self.parse()

        followers, last_user_reg_date = self._find_all_user_blocks(self.soup)
        for u in followers:
            if u.get_followers_num() >= 20 and u.get_location() == u"北京":
                yield u

        #pagination
        _xsrf = self.soup.find("input", attrs={'name': '_xsrf'})["value"]
        header = {
            'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
            'Host': "www.zhihu.com",
            'Referer': self.url,
        }

        followers_num = self.get_followers_num()
        print followers_num

        #followers_num = 1000

        for page_num in range(1,(followers_num-40)/20):
            print '\n*',
            sys.stdout.flush()
            time.sleep(0.1)
            data = {"offset":20+page_num*20,"start":last_user_reg_date,"_xsrf":_xsrf}
            try:
                r = requests.post(self.url, data=data, headers=header)
                response = simplejson.loads(r.content)
                html_body = BeautifulSoup(response["msg"][1].encode("utf-8"), "lxml")
                followers, last_user_reg_date = self._find_all_user_blocks(html_body)
                for u in followers:
                    try:
                        if u.get_followers_num() >= 20 and u.get_location() == u"北京":
                            print '.',
                            sys.stdout.flush()
                            yield u
                    except Exception, e:
                        continue
            except Exception, e:
                continue


def Usage(prog):
    return "Usage: Python ",prog,"topic id (example:19552212)"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print Usage(sys.argv[0])
    else:
        topic_id = sys.argv[1]
        with open(topic_id+".txt","w+") as f:
            followers = TopicFollowers("https://www.zhihu.com/topic/%s/followers"%topic_id)
            for u in followers.get_followers_raw():
                f.write(u.user_url+"\n")
                f.flush()




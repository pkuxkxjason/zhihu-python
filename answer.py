import os
import platform
import re

import html2text
import requests
from bs4 import BeautifulSoup

from question import Question
from user import User


class Answer:
    answer_url = None
    # session = None
    soup = None

    def __init__(self, answer_url, question=None, author=None, upvote=None, content=None):

        self.answer_url = answer_url
        if question != None:
            self.question = question
        if author != None:
            self.author = author
        if upvote != None:
            self.upvote = upvote
        if content != None:
            self.content = content

    def parser(self):
        r = requests.get(self.answer_url)
        soup = BeautifulSoup(r.content, "lxml")
        self.soup = soup

    def get_question(self):
        if hasattr(self, "question"):
            return self.question
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            question_link = soup.find("h2", class_="zm-item-title zm-editable-content").a
            url = "http://www.zhihu.com" + question_link["href"]
            title = question_link.string.encode("utf-8")
            question = Question(url, title)
            return question

    def get_author(self):
        if hasattr(self, "author"):
            return self.author
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            if soup.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
                author_url = None
                author = User(author_url)
            else:
                author_tag = soup.find("div", class_="zm-item-answer-author-info").find_all("a")[1]
                author_id = author_tag.string.encode("utf-8")
                author_url = "http://www.zhihu.com" + author_tag["href"]
                author = User(author_url, author_id)
            return author

    def get_upvote(self):
        if hasattr(self, "upvote"):
            return self.upvote
        else:
            if self.soup == None:
                self.parser()
            soup = self.soup
            count = soup.find("span", class_="count").string
            if count[-1] == "K":
                upvote = int(count[0:(len(count) - 1)]) * 1000
            elif count[-1] == "W":
                upvote = int(count[0:(len(count) - 1)]) * 10000
            else:
                upvote = int(count)
            return upvote

    def get_content(self):
        if hasattr(self, "content"):
            return self.content
        else:
            if self.soup == None:
                self.parser()
            soup = BeautifulSoup(self.soup.encode("utf-8"), "lxml")
            answer = soup.find("div", class_="zm-editable-content clearfix")
            soup.body.extract()
            soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
            soup.body.append(answer)
            img_list = soup.find_all("img", class_="content_image lazy")
            for img in img_list:
                img["src"] = img["data-actualsrc"]
            img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
            for img in img_list:
                img["src"] = img["data-actualsrc"]
            noscript_list = soup.find_all("noscript")
            for noscript in noscript_list:
                noscript.extract()
            content = soup
            self.content = content
            return content

    def to_txt(self):

        content = self.get_content()
        body = content.find("body")
        br_list = body.find_all("br")
        for br in br_list:
            br.insert_after(content.new_string("\n"))
        li_list = body.find_all("li")
        for li in li_list:
            li.insert_before(content.new_string("\n"))

        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "text"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write("\n\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "a")
                f.write(self.get_question().get_title() + "\n\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "text"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "text")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.txt"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            f = open(os.path.join(os.path.join(os.getcwd(), "text"), file_name), "wt")
            f.write(self.get_question().get_title() + "\n\n")
        if platform.system() == 'Windows':
            f.write("作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8').encode('gbk') + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("gbk"))
            link_str = "原链接: ".decode('utf-8').encode('gbk')
            f.write("\n" + link_str + self.answer_url.decode('utf-8').encode('gbk'))
        else:
            f.write("作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n\n")
            f.write(body.get_text().encode("utf-8"))
            f.write("\n" + "原链接: " + self.answer_url)
        f.close()

    # def to_html(self):
    # content = self.get_content()
    # if self.get_author().get_user_id() == "匿名用户":
    # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.html"
    # f = open(file_name, "wt")
    # print file_name
    # else:
    # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.html"
    # f = open(file_name, "wt")
    # print file_name
    # f.write(str(content))
    # f.close()

    def to_md(self):
        content = self.get_content()
        if platform.system() == 'Windows':
            anon_user_id = "匿名用户".decode('utf-8').encode('gbk')
        else:
            anon_user_id = "匿名用户"
        if self.get_author().get_user_id() == anon_user_id:
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if os.path.exists(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name)):
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("\n")
            else:
                f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "a")
                f.write("# " + self.get_question().get_title() + "\n")
        else:
            if not os.path.isdir(os.path.join(os.path.join(os.getcwd(), "markdown"))):
                os.makedirs(os.path.join(os.path.join(os.getcwd(), "markdown")))
            if platform.system() == 'Windows':
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md".decode(
                    'utf-8').encode('gbk')
            else:
                file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            print file_name
            # file_name = self.get_question().get_title() + "--" + self.get_author().get_user_id() + "的回答.md"
            # if platform.system() == 'Windows':
            # file_name = file_name.decode('utf-8').encode('gbk')
            # print file_name
            # else:
            # print file_name
            file_name = file_name.replace("/", "'SLASH'")
            f = open(os.path.join(os.path.join(os.getcwd(), "markdown"), file_name), "wt")
            f.write("# " + self.get_question().get_title() + "\n")
        if platform.system() == 'Windows':
            f.write("### 作者: ".decode('utf-8').encode('gbk') + self.get_author().get_user_id() + "  赞同: ".decode(
                'utf-8').encode('gbk') + str(self.get_upvote()) + "\n")
        else:
            f.write("### 作者: " + self.get_author().get_user_id() + "  赞同: " + str(self.get_upvote()) + "\n")
        text = html2text.html2text(content.decode('utf-8')).encode("utf-8")

        r = re.findall(r'\*\*(.*?)\*\*', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'_(.*)_', text)
        for i in r:
            if i != " ":
                text = text.replace(i, i.strip())

        r = re.findall(r'!\[\]\((?:.*?)\)', text)
        for i in r:
            text = text.replace(i, i + "\n\n")

        if platform.system() == 'Windows':
            f.write(text.decode('utf-8').encode('gbk'))
            link_str = "\n---\n#### 原链接: ".decode('utf-8').encode('gbk')
            f.write(link_str + self.answer_url.decode('utf-8').encode('gbk'))
        else:
            f.write(text)
            f.write("\n---\n#### 原链接: " + self.answer_url)
        f.close()

    def get_visit_times(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        for tag_p in soup.find_all("p"):
            if "所属问题被浏览" in tag_p.contents[0].encode('utf-8'):
                return int(tag_p.contents[1].contents[0])

    def get_voters(self):
        if self.soup == None:
            self.parser()
        soup = self.soup
        data_aid = soup.find("div", class_="zm-item-answer  zm-item-expanded")["data-aid"]
        request_url = 'http://www.zhihu.com/node/AnswerFullVoteInfoV2'
        # if session == None:
        #     create_session()
        # s = session
        # r = s.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)})
        r = requests.get(request_url, params={"params": "{\"answer_id\":\"%d\"}" % int(data_aid)})
        soup = BeautifulSoup(r.content, "lxml")
        voters_info = soup.find_all("span")[1:-1]
        if len(voters_info) == 0:
            return
            yield
        else:
            for voter_info in voters_info:
                if voter_info.string == u"匿名用户、" or voter_info.string == u"匿名用户":
                    voter_url = None
                    yield User(voter_url)
                else:
                    voter_url = "http://www.zhihu.com" + str(voter_info.a["href"])
                    voter_id = voter_info.a["title"].encode("utf-8")
                    yield User(voter_url, voter_id)
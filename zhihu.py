# -*- coding: utf-8 -*-
'''

                                                                                         ;$$;
                                                                                    #############
                                                                               #############;#####o
                                                      ##                 o#########################
                                                      #####         $###############################
                                                      ##  ###$ ######!    ##########################
                           ##                        ###    $###          ################### ######
                           ###                      ###                   ##o#######################
                          ######                  ;###                    #### #####################
                          ##  ###             ######                       ######&&################
                          ##    ###      ######                            ## ############ #######
                         o##      ########                                  ## ##################
                         ##o                ###                             #### #######o#######
                         ##               ######                             ###########&#####
                         ##                ####                               #############!
                        ###                                                     #########
               #####&   ##                                                      o####
             ######     ##                                                   ####*
                  ##   !##                                               #####
                   ##  ##*                                            ####; ##
                    #####                                          #####o   #####
                     ####                                        ### ###   $###o
                      ###                                            ## ####! $###
                      ##                                            #####
                      ##                                            ##
                     ;##                                           ###                           ;
                     ##$                                           ##
                #######                                            ##
            #####   &##                                            ##
          ###       ###                                           ###
         ###      ###                                             ##
         ##     ;##                                               ##
         ##    ###                                                ##
          ### ###                                                 ##
            ####                                                  ##
             ###                                                  ##
             ##;                                                  ##
             ##$                                                 ##&
              ##                                                 ##
              ##;                                               ##
               ##                                              ##;
                ###                                          ###         ##$
                  ###                                      ###           ##
   ######################                              #####&&&&&&&&&&&&###
 ###        $#####$     ############&$o$&################################
 #                               $&########&o
'''

# Build-in / Std
import cookielib
import sys

# requirements
import requests

try:
    from bs4 import BeautifulSoup
except:
    import BeautifulSoup

# module
from auth import islogin,login
from mylogging import MyLogging

"""
    Note:
        1. 身份验证由 `auth.py` 完成。
        2. 身份信息保存在当前目录的 `cookies` 文件中。
        3. `requests` 对象可以直接使用，身份信息已经自动加载。

    By Luozijun (https://github.com/LuoZijun), 09/09 2015

"""

login()

requests = requests.Session()
requests.cookies = cookielib.LWPCookieJar('cookies')
try:
    requests.cookies.load(ignore_discard=True)
except:
    MyLogging.error(u"你还没有登录知乎哦 ...")
    MyLogging.info(u"执行 `python auth.py` 即可以完成登录。")
    raise Exception("无权限(403)")


if islogin() != True:
    MyLogging.error(u"你的身份信息已经失效，请重新生成身份信息( `python auth.py` )。")
    raise Exception("无权限(403)")


reload(sys)
sys.setdefaultencoding('utf8')


class Zhihu(object):
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.parse()

    def parse(self):
        if not self.soup:
            r = requests.get(self.url)
            self.soup = BeautifulSoup(r.content, "lxml")



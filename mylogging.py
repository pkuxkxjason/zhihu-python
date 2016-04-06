# -*- coding: utf-8 -*-

import termcolor

class MyLogging:
    flag = True

    @staticmethod
    def error(msg):
        if MyLogging.flag == True:
            print "".join(  [ termcolor.colored("ERROR", "red"), ": ", termcolor.colored(msg, "white") ] )
    @staticmethod
    def warn(msg):
        if MyLogging.flag == True:
            print "".join(  [ termcolor.colored("WARN", "yellow"), ": ", termcolor.colored(msg, "white") ] )
    @staticmethod
    def info(msg):
        # attrs=['reverse', 'blink']
        if MyLogging.flag == True:
            print "".join(  [ termcolor.colored("INFO", "magenta"), ": ", termcolor.colored(msg, "white") ] )
    @staticmethod
    def debug(msg):
        if MyLogging.flag == True:
            print "".join(  [ termcolor.colored("DEBUG", "magenta"), ": ", termcolor.colored(msg, "white") ] )
    @staticmethod
    def success(msg):
        if MyLogging.flag == True:
            print "".join(  [ termcolor.colored("SUCCES", "green"), ": ", termcolor.colored(msg, "white") ] )



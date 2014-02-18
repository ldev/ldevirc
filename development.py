#!/usr/bin/python
# -*- coding: utf-8 -*-


# This is a python bot written by Jonas Lindstad (LDEV)
# You are free to use this code, which is licensed under the "WTFPL license".
#
# ---------------------------------------------------------------------
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                   Version 2, December 2004
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
#
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
# 
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
# 
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#
# ---------------------------------------------------------------------
#
#
# TODO:
# * http://stackoverflow.com/questions/930700/python-parsing-irc-messages
# * Få nick-greia inn i en while-løkke, som sikrer at den får et unikt brukernavn
# * Append users to auto-op file from IRC channel
# * Skille ut config i egen fil

#
# MODULES
#
import socket
import sys
from random import choice
import time
import datetime
import logging
import logging.handlers # why?
from subprocess import Popen, PIPE # For calling traceroute
import signal # for ctrl-c catching
import sys # for ctrl-c catching
from platform import platform # Finne linuxversjon etc.
from os import path # finding the current script path

# import urllib2 # URL grabbing
import simplejson as json # Config parsing
import re # URL grabbing
from urllib.request import urlopen # URL grabbing


#
# VARIABLES
#
version = 'ldevirc 0.1 testing'
working_dir = path.dirname(path.realpath(__file__)) # no trailing slash

# load configuration file
with open('%s/config.json' % working_dir) as data_file:    
    config = json.load(data_file)

#
# LOGGING
# Good article about logging: http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python
# logger.<level> = debug, info, warn, error
#
logger_file = '%s/logs/%s_%s' % (working_dir, config['network'].lower(), config['channel'].lower())
logger = logging.getLogger(version)
logger_level = logging.getLevelName(config['logging']['level'])
# logger.setLevel(logging.DEBUG)
logger.setLevel(logger_level)
handler = logging.handlers.RotatingFileHandler(logger_file, 'a', maxBytes=config['logging']['max_file_size'], backupCount=config['logging']['max_number_of_files'], encoding="utf-8")
# handler.setLevel(logging.DEBUG)
handler.setLevel(logger_level)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # left "%(name)" out on purpose
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info('%s started' % version)



#
# FUNCTIONS
#
def find_user(str):
    return str.split('!')[0][1:]
    
def traceroute(dest, user):
    dest = dest.replace('|', '').replace(';', '').replace('&', '') # somewhat securing against malicious input..
    irc_cmd('PRIVMSG %s :Performing trace towards %s\r\n' % (user, dest))
    trace_log_text = "Performing traceroute towards %s (requested by %s)" % (dest, user)
    logger.info(trace_log_text)
    p = Popen(['tracepath', dest], stdout=PIPE)
    while True:
        line = p.stdout.readline() # return bytes
        if not line:
            break
        line = line.decode("utf-8")
        irc.send(('PRIVMSG %s :%s\r\n' % (user, line)).encode()) # to remove b'' from line

# send string to IRC server
def irc_cmd(text):
    irc.send(("%s\r\n" % text).encode(config['server_encoding']))
    
def timestamp():
    return datetime.datetime.now().isoformat().split('.')[0]

# handle ctrl+c gracefully
def signal_handler(signal, frame):
    print ('\nctrl+c detected. Disconnecting from %s' % config['server'])
    logger.warn(text.strip())
    irc_cmd("QUIT :%s" % config['quit_message'])
    time.sleep(1)
    sys.exit(0)
    
def grab_title(url):
    source = urlopen(url).read().decode('utf-8')
    match = re.findall(r'<title>(.*)</title>', source)
    if match:
        irc_cmd('PRIVMSG %s :Tittel: %s' % (config['channel'], match[0]))
        return match[0]
        # for link, title in match:
        #     print "link %s -> %s" % (link, title)
    else:
        logger.info('No match')
    
#
# PERFORM IRC CONNECTION
#

# register signal handling (ctrl+c)
signal.signal(signal.SIGINT, signal_handler)
print ('\r\npress ctrl+c to close the connection to the server')


irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logger.info("ldevirc connecting to %s (%s)" % (config['network'], config['server']))
irc.connect((config['server'], config['port']))

irc_cmd('USER %s Testing 0 * :...' % (config['botnick']))
time.sleep(1) # Prevent Excess flood at a couple of networks (EFnet for instance)

irc_cmd('NICK %s' % config['botnick'])
time.sleep(1) # Prevent Excess flood at a couple of networks (EFnet for instance)

#
# TODO: Replace with while-loop of some sort
#
text = irc.recv(4096).decode(config['server_encoding'])
if text.find('ERR_ALREADYREGISTRED') != -1:
    logger.info('Nick %s taken. Attempting to use %s-' % (config['botnick'], config['botnick']))
    irc_cmd('NICK %s-' % config['botnick'])
else:
    logger.info('Registered nick %s' % config['botnick'])
# prevents loop if the server closed the connection
if text.find('ERROR') !=-1:
    # print('[%s] ERROR: %s' % timestamp(), text)
    log.error('%s' % text)
    sys.exit(1)

# join channel
irc_cmd("JOIN %s" % config['channel'])
logger.info("Joined channel %s" % config['channel'])

#
# MAIN LOOP - PROCESSING
#
while 1:
    # receive data from IRC server
    text = irc.recv(4096).decode(config['server_encoding'])
    if len(text.strip()) == 0:
        logger.error('No data from IRC server - Either IRC server disconnected client or server crashed')
        sys.exit(1)
    
    # print text to terminal
    for line in text.split('\n'):
        if len(line.strip()) > 0:
            if text.find(config['botnick']) != -1:
                print('[%s] %s' % (timestamp(), line.strip()))
                logger.info(line.strip())
            else:
                logger.debug(line.strip())
    
    #
    # BOT CONTROL
    #
    if text.find('PING') != -1:
        logger.debug('PONG %s' % (text.split()[1]))
        irc_cmd(('PONG %s' % (text.split()[1])))
        
        
        
    # Join on kick
    if text.find('KICK %s %s' % (config['channel'], config['botnick'])):
        if text.split(' ')[1] == 'KICK' and text.split(' ')[2] == channel and text.split(' ')[3] == config['botnick']:
            logger.warn(text)
            time.sleep(1)
            irc_cmd("JOIN %s" % config['channel'])
            time.sleep(0.5)
            irc_cmd('PRIVMSG %s :I\'m back, bitches!' % config['channel'])
    
    #
    # CTCP
    # http://www.irchelp.org/irchelp/rfc/ctcpspec.html
    # http://www.kvirc.net/doc/doc_ctcp_handling.html
    # Skipped CTCP commands: SOURCE, USERINFO, ERRMSG
    #
    
    # FINGER - Returns the user's full name, and idle time
    if text.find('PRIVMSG %s :\u0001FINGER\u0001' % (config['botnick'])) != -1:
        logger.debug('NOTICE %s :\u0001FINGER %s by ldev.no\u0001' % (find_user(text), config['botnick']))
        irc_cmd('NOTICE %s :\u0001FINGER %s by ldev.no\u0001' % (find_user(text), config['botnick']))
        
    # VERSION - The version and type of the client
    if text.find('PRIVMSG %s :\u0001VERSION\u0001' % (config['botnick'])) != -1:
        logger.debug('NOTICE %s :\u0001VERSION %s:%s\u0001' % (find_user(text), version, platform()))
        irc_cmd('NOTICE %s :\u0001VERSION %s:%s\u0001' % (find_user(text), version, platform()))
    
    # CLIENTINFO - Dynamic master index of what a client knows
    if text.find('PRIVMSG %s :\u0001CLIENTINFO\u0001' % (config['botnick'])) != -1:
        logger.debug('NOTICE %s :\u0001VERSION %s under development by Jonas Lindstad\u0001' % version)
        irc_cmd('NOTICE %s :\u0001VERSION %s under development by Jonas Lindstad\u0001' % version)

    # PING - Used to measure the delay of the IRC network between clients.
    if text.find('PRIVMSG %s :\u0001PING\u0001' % (config['botnick'])) != -1:
        logger.debug('NOTICE %s :\u0001PING %s\u0001' % (text.split()[2]))
        irc_cmd('NOTICE %s :\u0001PING %s\u0001' % (text.split()[2]))

    # TIME - Gets the local date and time from other clients.
    if text.find('PRIVMSG %s :\u0001TIME\u0001' % (config['botnick'])) != -1:
        logger.debug('NOTICE %s :\u0001TIME %s\u0001' % timestamp())
        irc_cmd('NOTICE %s :\u0001TIME %s\u0001' % timestamp())


        
    #
    # CAP - capabilities
    # http://www.leeh.co.uk/draft-mitchell-irc-capabilities-02.html
    #
    

    #
    # All the extra shit
    #
    
    # help
    if text.find('!help') !=-1 and text.find(config['botnick']) == -1:
        logger.info('PRIVMSG %s :This is %s. Commands: !help, !bully <user>, !trace <host>' % (config['channel'], version))
        irc_cmd('PRIVMSG %s :This is %s. Commands: !help, !bully <user>, !trace <host>' % (config['channel'], version))
    
    # bully
    if text.find(':!bully') != -1:
        with open('%s/bully.txt' % working_dir) as f:
            lines = f.read().splitlines()
        to = text.split(':!bully')[1].strip()
        phrase = choice(lines)
        logger.info('PRIVMSG %s :%s %s' % (config['channel'], to, phrase))
        irc_cmd('PRIVMSG %s :%s %s' % (config['channel'], to, phrase))
    
    # gay
    if text.find('gay') !=-1 and text.find(config['botnick']) == -1:
        logger.info('PRIVMSG %s :%s er gay!' % (config['channel'], find_user(text)))
        irc_cmd('PRIVMSG %s :%s er gay!' % (config['channel'], find_user(text)))
    
    # auto OP
    if text.find("JOIN :%s" % config['channel']) !=-1 and text.find(config['botnick']) == -1:
        auto_op_file = '%s/auto-op/%s_%s' % (working_dir, network.lower(), channel.lower())
        logger.debug('Checking auto-op file "%s"' % auto_op_file)
        if path.isfile(auto_op_file):
            with open(auto_op_file) as f:
                operators = f.read().splitlines()
            if any(ext in text for ext in operators):
                to = text.split('!')[0][1:]
                irc_cmd(('PRIVMSG %s :Hei, deg kjenner jeg!' % config['channel']))
                logger.info(('MODE %s +o %s' % (config['channel'], to)))
                irc_cmd(('MODE %s +o %s' % (config['channel'], to)))
            else:
                logger.debug('User not in auto-op file')
        else:
            logger.debug('No auto-op file for this network/channel')
        
    # trace
    if text.find(':!trace') != -1:
        dest = text.split(':!trace')[1].strip()
        traceroute(dest, find_user(text))
        
    # URL title grabber
    if text.find('http://') != -1 or text.find('https://') != -1:
        urls = re.findall(r'(https?://\S+)', text)
        logger.info('Fetching <title> from URL %s' % urls[0])
        try:
            print(grab_title(urls[0]))
        except:
            logger.info('Failed to fetch <title>. Probably 404/not UTF-8 encoding')
            pass
        # irc_cmd('PRIVMSG %s :URL: %s' % (config['channel'], urls[0]))
        # try:
        #     grab_title(urls[0])
        # except:
        #     pass
        # ['http://tinyurl.com/blah', 'http://blabla.com']

# -*- coding: utf-8 -*-

# Se http://stackoverflow.com/questions/2968408/how-do-i-program-a-simple-irc-bot-in-python for mer info

# Todo:
# * http://stackoverflow.com/questions/930700/python-parsing-irc-messages
# * Få nick-greia inn i en while-løkke, som sikrer at den får et unikt brukernavn

import socket
import sys
from random import choice
import time
import datetime

# For calling traceroute
from subprocess import Popen, PIPE

# for ctrl-c catching
import signal
import sys

# Finne linuxversjon etc.
from platform import platform

# finding the current script path
import os

# server = "irc.opasia.dk"
server = 'irc.underworld.no'
network = 'efnet'
channel = '#X'

botnick = "X"
port = 6667
server_encoding = 'latin-1'
version = 'ldevirc 0.1 testing'

working_dir = os.path.dirname(os.path.realpath(__file__)) # no trailing slash

#
# Functions
#
def find_user(str):
    return str.split('!')[0][1:]
    
def traceroute(dest, user):
    dest = dest.replace('|', '').replace(';', '').replace('&', '') # somewhat securing against malicious input..
    # irc.send(('PRIVMSG %s :Performing trace towards %s\r\n' % (user, dest)).encode())
    irc_cmd('PRIVMSG %s :Performing trace towards %s\r\n' % (user, dest))
    trace_log_text = "Performing traceroute towards %s (requested by %s)" % (dest, user)
    print("[%s] %s" % (timestamp(), trace_log_text))
    p = Popen(['tracepath', dest], stdout=PIPE)
    while True:
        line = p.stdout.readline() # return bytes
        if not line:
            break
        line = line.decode("utf-8")
        irc.send(('PRIVMSG %s :%s\r\n' % (user, line)).encode()) # to remove b'' from line

def irc_cmd(text):
    # print string. Debuging/logging purposes
    print ("[%s] %s" % (timestamp(), text))
    
    # send string to IRC server
    irc.send(("%s\r\n" % text).encode(server_encoding))
    
def timestamp():
    return datetime.datetime.now().isoformat().split('.')[0]

# handle ctrl+c gracefully
def signal_handler(signal, frame):
    print ('\nctrl+c detected. Disconnecting from %s' % server)
    irc_cmd("QUIT :Disconnecting from IRC")
    time.sleep(1)
    sys.exit(0)
    
    
#
# Connect to the IRC server
#

# register signal handling (ctrl+c)
print ('\r\npress ctrl+c to close the connection to the server')
signal.signal(signal.SIGINT, signal_handler)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print ("[%s] ldevirc connecting to %s (%s)" % (timestamp(), network, server))
irc.connect((server, port))

# set user parameters
irc_cmd('USER %s Testing 0 * :...' % (botnick))
time.sleep(1) # unngå excess flood

irc_cmd('NICK %s' % botnick)
time.sleep(1) # prevents excess flood at EFnet

text = irc.recv(4096).decode('latin-1')
if text.find('ERR_ALREADYREGISTRED') != -1:
    irc_cmd('NICK %s-' % botnick)

# prevents eternal loop
if text.find('ERROR') !=-1:
    print('[%s] ERROR: %s' % timestamp(), text)
    sys.exit(1)

# join channel
irc_cmd("JOIN %s" % channel)

#
# MAIN LOOP - PROCESSING
#
while 1:
    # receive data from IRC server
    text = irc.recv(4096).decode('latin-1')
    if len(text.strip()) == 0:
        print('[%s] No data from IRC server - Either IRC server disconnected client or server crashed' % timestamp())
        sys.exit(1)
    
    # print text to terminal
    print('[%s] %s' % (timestamp(), text))
    
    # basic ping/pong replies to server
    if text.find('PING') != -1:
        irc_cmd(('PONG %s' % (text.split()[1])))
    #
    # CTCP
    # http://www.irchelp.org/irchelp/rfc/ctcpspec.html
    # http://www.kvirc.net/doc/doc_ctcp_handling.html
    # Skipped CTCP commands: SOURCE, USERINFO, ERRMSG
    #
    
    # FINGER - Returns the user's full name, and idle time
    if text.find('PRIVMSG %s :\u0001FINGER\u0001' % (botnick)) != -1:
        irc_cmd('NOTICE %s :\u0001FINGER %s by ldev.no\u0001' % (find_user(text), botnick))
        
    # VERSION - The version and type of the client
    if text.find('PRIVMSG %s :\u0001VERSION\u0001' % (botnick)) != -1:
        irc_cmd('NOTICE %s :\u0001VERSION %s:%s\u0001' % (find_user(text), version, platform()))
    
    # CLIENTINFO - Dynamic master index of what a client knows
    if text.find('PRIVMSG %s :\u0001CLIENTINFO\u0001' % (botnick)) != -1:
        irc_cmd('NOTICE %s :\u0001VERSION %s under development by Jonas Lindstad\u0001' % version)

    # PING - Used to measure the delay of the IRC network between clients.
    if text.find('PRIVMSG %s :\u0001PING\u0001' % (botnick)) != -1:
        irc_cmd('NOTICE %s :\u0001PING %s\u0001' % (text.split()[2]))

    # TIME - Gets the local date and time from other clients.
    if text.find('PRIVMSG %s :\u0001TIME\u0001' % (botnick)) != -1:
        irc_cmd('NOTICE %s :\u0001TIME %s\u0001' % timestamp())


        
    #
    # CAP - capabilities
    # http://www.leeh.co.uk/draft-mitchell-irc-capabilities-02.html
    #
    
    
    
    
    #
    # All the extra shit
    #
    
    # help
    if text.find('!help') !=-1 and text.find(botnick) == -1:
        irc_cmd('PRIVMSG %s :This is %s. Commands: !help, !bully <user>, !trace <host>' % (channel, version))
    
    # bully
    if text.find(':!bully') != -1:
        with open('%s/bully.txt' % working_dir) as f:
            lines = f.read().splitlines()
        to = text.split(':!bully')[1].strip()
        irc_cmd('PRIVMSG %s :%s %s' % (channel, to, choice(lines)))
    
    # gay
    if text.find('gay') !=-1 and text.find(botnick) == -1:
        irc_cmd('PRIVMSG %s :%s er gay!' % (channel, find_user(text)))
    
    # auto OP
    if text.find("JOIN :%s" % channel) !=-1 and text.find(botnick) == -1:
        auto_op_file = '%s/auto-op/%s_%s' % (working_dir, network.lower(), channel.lower())
        print('[%s] Checking auto-op file "%s"' % (timestamp(),  auto_op_file))
        if os.path.isfile(auto_op_file):
            with open(auto_op_file) as f:
                operators = f.read().splitlines()
            if any(ext in text for ext in operators):
                to = text.split('!')[0][1:]
                irc_cmd(('PRIVMSG %s :Hei, deg kjenner jeg!' % channel))
                irc_cmd(('MODE %s +o %s' % (channel, to)))
            else:
                print('[%s] User not in auto-op file' % timestamp())
        else:
            print('[%s] No auto-op file for this network/channel' % timestamp())
        
    # trace
    if text.find(':!trace') != -1:
        dest = text.split(':!trace')[1].strip()
        traceroute(dest, find_user(text))
# -*- coding: utf-8 -*-

# Se http://stackoverflow.com/questions/2968408/how-do-i-program-a-simple-irc-bot-in-python for mer info


# Todo:
# * http://stackoverflow.com/questions/930700/python-parsing-irc-messages
# * Legge til hosten i .nl
# * Sleep og få inn støtte for EFnet

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

server = "irc.opasia.dk"
channel = "#no-shitbull"
botnick = "PythonFu"
port = 6667

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print ("connecting to: %s" % (server))
irc.connect((server, port))

# handle ctrl+c gracefully
def signal_handler(signal, frame):
	print ('\nctrl+c detected. Disconnecting from %s' % server)
	irc.send("QUIT :Disconnecting from IRC\n".encode('latin-1'))
	time.sleep(1)
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
print ('\r\npress ctrl+c to close the connection to the server')

irc.send(("USER \"%s\" 0 * :jonaslindstad@gmail.com\n" % (botnick)).encode('latin-1')) # set username
irc.send(("NICK %s\n" % botnick).encode('latin-1')) # set nick
irc.send(("JOIN %s\n" % channel).encode('latin-1')) # join channel
setninger = [
	'lukter godt',
	'smaker kebab',
	'liker godt voksne kvinner med bart',
	'tenker på goatse-rumpa når han tar på seg selv',
	'vil leke med vaskedama',
	'er flink til å putte hele bananer ned i halsen',
	'har generelt sett mer intens tålukt enn gjennomsnittet',
	'forstår seg ikke på sånn internett',
	'vurderer penis-implantat',
	'har ikke gagrefleks lenger',
	'er litt usikker på hvilket hull som egentlig er vaginaen',
	'var fornøyd med årets ribbe',
	'har tre testikler',
	'gleder seg til den dagen han ser en naken kvinne for første gang',
	'tisser på doringen fordi det er gøy',
	'har en oppblåsbar sau hjemme',
	'får plass til en colaboks i anus',
	', også kjent som einstøtaren',
	'liker ikke appelsin',
	'synes fiskepinner er helt ok, men foretrekker pikk',
	'er en tennbrikett som ikke hører hjemme noe sted',
	'er skarp som en smørekriv',
	'tror vaskedama ikke dusjer',
	'synes det er mer enn nok å dusje en gang i måneden',
	'skulle ønske prompene sine ikke svei sånn i øya',
	'synes bajs, tiss og prump er like morsomt som denne boten her..',
	'vurderer plastisk kirurgi for å endelig få seg sammenhengende øyenbryn',
	'elsker maten i kantina - dagens høydepunkt',
	'liker håret i dusjsluket',
	'er flink til å bake vafler',
	'er redd for eple',
	'har mareritt om hufsa',
	'synes snorkfrøken er sexy',
	'dikter poesi på fritiden',
	'synes hest er et fint dyr',
	'liker bluewaffles',
	'foretrekker en god runde sitronfest',
	'blomstrer idag',
	'lyser opp verdens tunge dager',
	'makes me happy',
	'er sofistikert i pyjamas',
	'er et svært trivlig menneske som sprer idyll og sjarm',
	'smaker agurk'
]

op_strings = [
	'@cm-84.209.89.18.getinternet.no',
	'@ext2.osl.no.ip.tdc.net',
	'@ext2.osl.no.ip.tdc.net'
]

def find_user(str):
	return str.split('!')[0][1:]
	
def traceroute(dest, user):
	dest = dest.replace('|', '').replace(';', '').replace('&', '')
	irc.send(('PRIVMSG %s :Performing trace towards %s\r\n' % (user, dest)).encode())
	print("Performing traceroute towards %s (requested by %s)" % (dest, user))
	p = Popen(['tracepath', dest], stdout=PIPE)
	while True:
		line = p.stdout.readline() # return bytes
		if not line:
			break
		line = line.decode("utf-8")
		irc.send(('PRIVMSG %s :%s\r\n' % (user, line)).encode())

while 1:
	text = irc.recv(4096).decode('latin-1')
	
	# timestamp
	st = str(datetime.datetime.now().isoformat()).split('.')[0]
	print ("[%s] %s" % (st, text))
	
	if text.find('PING') != -1:
		irc.send(('PONG %s\r\n' % (text.split()[1])).encode('latin-1'))
	if text.find(':!mobb') != -1:
		to = text.split(':!mobb')[1].strip()
		# to = t[1].strip()
		phrase = choice(setninger)
		irc.send(('PRIVMSG %s :%s %s \r\n' % (channel, to, phrase)).encode('latin-1'))
	if text.find('gay') !=-1:
		# for å unngå evige loops
		if(text.find(botnick)) == -1:
			irc.send(('PRIVMSG %s :%s er gay!\r\n' % (channel, find_user(text))).encode('latin-1'))
	if text.find("JOIN :%s" % channel) !=-1:
		if(text.find(botnick)) == -1:
			if any(ext in text for ext in op_strings):
				to = text.split('!')[0][1:]
				# to = t[0]
				# to = str(to[1:])
				irc.send(('PRIVMSG %s :Hei, deg kjenner jeg!\r\n' % channel).encode('latin-1'))
				irc.send(('MODE %s +o %s\r\n' % (channel, to)).encode('latin-1'))
				
				
				
	if text.find(':!trace') != -1:
		irc.send(('PRIVMSG %s :Starter trace...\r\n' % find_user(text)).encode('latin-1'))
		dest = text.split(':!trace')[1].strip()
		traceroute(dest, find_user(text))
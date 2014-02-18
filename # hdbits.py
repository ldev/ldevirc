# -*- coding: utf-8 -*-

# Se http://stackoverflow.com/questions/2968408/how-do-i-program-a-simple-irc-bot-in-python for mer info

import socket
import sys
from random import choice

server = "irc.inet.tele.dk"
channel = "#hdbits.org"
botnick = "PythonFu"
port = 6666

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket
print ("connecting to: %s" % (server))
irc.connect((server, port))
# irc.send("USER "+ botnick +" "+ botnick +" "+ botnick +" :Testing\n")

send_string = "USER \"%s\" \"%s\" \"%s\" :Testing\n" % (botnick, botnick, botnick)
irc.send(send_string.encode('latin-1'))

send_string = "NICK "+ botnick +"\n"
irc.send(send_string.encode('latin-1'))

# send_string = "PRIVMSG nickserv :iNOOPE\r\n"
# irc.send(send_string.encode('latin-1'))

send_string = "JOIN "+ channel +"\n"
irc.send(send_string.encode('latin-1'))

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
	', også kjent som einstøtern',
	'liker ikke appelsin',
	'synes fiskepinner er helt ok, men foretrekker pikk',
	'er en tennbrikett som ikke hører hjemme noe sted',
	'er skarp som en smørekriv',
	'tror vaskedama ikke dusjer',
	'synes det er mer enn nok å dusje en gang i måneden',
	'skulle ønske prompene sine ikke svei sånn i øya',
	'synes bajs, tiss og prump er like morsomt som denne boten her..',
]

while 1:
	text = irc.recv(4096).decode('latin-1')
	print (text, "\n")

	if text.find('PING') != -1:
		send_string = 'PONG ' + text.split() [1] + '\r\n'
		irc.send(send_string.encode('latin-1'))
	
	if text.find(':!mobb') != -1:
		t = text.split(':!mobb')
		to = t[1].strip() #this code is for getting the first word after !hi
		send_string = 'PRIVMSG '+channel+' :'+str(to)+' '+ choice(setninger) +' \r\n'
		irc.send(send_string.encode('latin-1'))
		
	if text.find('gay') !=-1:
		# for å unngå evige loops
		if(text.find(botnick)) == -1:
			t = text.split('!')
			to = t[0]
			to = to[1:]
			send_string = 'PRIVMSG '+channel+' :'+str(to)+' er gay! \r\n'
			irc.send(send_string.encode('latin-1'))
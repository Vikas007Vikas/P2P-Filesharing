import socket
import os
import hashlib
import time
import platform
import random
from datetime import datetime
import re
import json
from stat import *
def create_port(socket):
    np = random.randint(1000, 9999)
    try:
        socket.bind((host, np))
    except:
        return create_port(socket)
    return np
def shortlist(s,args):
	s.send('recieved')
	div = args.split()
	strt_time = int(div[2])
	end_time = int(div[3])
	cmd = "ls"
	result = os.popen(cmd).read()
	files = result.split()
	#print files
	num = len(files)
	i=0
	while i<num:
		filename = files[i]
		Timestamp = time.ctime(os.path.getmtime(files[i]))
		divide = Timestamp.split()
		month = divide[1]
		time1 = divide[3]
		date = int(divide[2])
		spl = time1.split(':')
		hour = int(spl[0])
		minut = int(spl[1])
		sec = int(spl[2])
		if month == 'Mar':
			val = 3
		elif month == 'Apr':
			val = 4
		tottime = val*30*24*60*60 + date*24*60*60 + hour*60*60 + minut*60 + sec #total time in seconds
		#print tottime
		if tottime >= strt_time and tottime <= end_time:
			fil = '"' + filename + '"'
			cmd = "stat --printf 'Type: %F\t' " + fil
			statbuff = os.stat(filename)
			size = str(statbuff.st_size)
			Type = os.popen(cmd).read()
			totstr = 'name:'+filename + '\t' +'size:' + size + '\t' + Type + '\t' + 'timestamp:' + Timestamp
			#print totstr
			s.send(totstr)
			#print totstr
			data = s.recv(1024)
		i = i+1
	s.send('done')

def regex(s,args):
	s.send('recieved')
	div = args.split()
	regx = div[2]
	#print regx
	cmd = 'ls'
	result = os.popen(cmd).read()
	files = result.split()
	num = len(files)
	i=0
	while i<num:
		if re.search(regx,files[i]) != None and re.search(regx,files[i]) != '':
			filename = files[i]
			Timestamp = time.ctime(os.path.getmtime(files[i]))
			statbuff = os.stat(files[i])
			size = str(statbuff.st_size)
			fil = '"' + filename + '"'
			cmd = "stat --printf 'Type: %F\t' " + fil
			Type = os.popen(cmd).read()
			totstr = 'name:'+filename + '\t' +'size:' + size + '\t' + Type + '\t' + 'timestamp:' + Timestamp
			s.send(totstr)
			data = s.recv(1024)
		i = i+1
	s.send('done')

def longlist(s,args):
	s.send("recieved")
	cmd = "ls"
	result = os.popen(cmd).read()
	files = result.split()
	#print files
	num = len(files)
	i=0
	while i<num:
		filename = files[i]
		statbuff = os.stat(files[i])
		size = str(statbuff.st_size)
		Timestamp1 = str(statbuff.st_mtime)
		Timestamp = time.ctime(os.path.getmtime(files[i]))
		#print Timestamp
		fil = '"' + filename + '"'
		cmd = "stat --printf 'Type: %F\t' " + fil
		Type = os.popen(cmd).read()
		totstr = 'name:'+filename + '\t' +'size:' + size + '\t' + Type + '\t' + 'timestamp:' + Timestamp
		s.send(totstr)
		#print totstr
		data = s.recv(1024)
		i = i+1
	s.send('done')

def send_filehash(s , filename):
	s.send("recieved")
	fil = '"' + filename + '"'
	cmd = "stat --printf '%F' " + fil
	Type = os.popen(cmd).read()
	if Type == 'directory':
		file_hash = '-1'
	elif Type == 'regular file':
		file_hash = os.popen('cksum "' + filename + '"').read().split()[0]
	Timestamp = time.ctime(os.path.getmtime(filename))
	totstr = file_hash + '\t' + 'lastmodifiedtime:' + Timestamp
	s.send(totstr)
	data = s.recv(1024)
	if data == 'recieved':
		print 'done sending hash'
	#command = "stat --printf 'Timestamp:%z\n' " + filename
	#statbuff = os.stat(filename)
	#stat = statbuff.st_mtime
	#result = str(stat)
	#result = os.popen(command).read()
	#s.send(result)
		#s.send('done')
def send_allhash(s,checker):
	#print 'abc'
	#print checker
	checker = str(checker)
	s.send("recieved")
	cmd = "ls"
	result = os.popen(cmd).read()
	files = result.split()

	#print files
	num = len(files)
	i=0
	while i<num:
		fil = '"' + files[i] + '"'
		cmd = "stat --printf '%F' " + fil
		Type = os.popen(cmd).read()
		if Type == 'directory':
			hash_value = '-1'
		elif Type == 'regular file':
			hash_value = os.popen(checker + ' ' + '"' + files[i] + '"').read().split()[0]
		#print hash_value
		#command = "stat --printf 'Timestamp:%z\n' " + files[i]
		statbuff = os.stat(files[i])
		stat = statbuff.st_mtime
		Timestamp = time.ctime(os.path.getmtime(files[i]))
		res = 'lastmodifiedtime:' + Timestamp + '\t' + hash_value + '\t' + files[i]
		#res = os.popen(command).read()
		s.send(res)
		#print res
		data = s.recv(1024)
		#print data
		#if data == 'gotit':
		#	print 'sent modified time'
		#s.send(files[i])
		#data1 = s.recv(1024)
		#if data == 'gotfile':
		#	print 'sent filename'
		i = i+1
	s.send('done')
def sendfile(s , args):
	div = args.split()
	protocol = div[1]
	filename = " ".join(div[2:])
	if (os.popen('ls "' + filename + '"').read().split('\n')[0] == ""):
		print 'file not opened'
		print 'No Such File or Directory'
		return
	data = s.send("recieved")
	#print data
	if protocol == 'UDP':
		ns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		new_port = create_port(ns)
		s.send(str(new_port))
		data, addr = ns.recvfrom(1024)
		print data
		if data == "recieved":
			file_hash = os.popen('md5sum "' + filename + '"').read().split()[0] 
			ns.sendto(file_hash,addr)
			#print 'passed'
			confirm1 = ns.recvfrom(1024)
			#print 'passes'
			confirm = confirm1[0]
			#print confirm
			if confirm == 'hashsame':
				perm1 = str(oct(os.stat(filename)[ST_MODE])[-3:])
				#print perm1
				perm = 'nodatasent ' + perm1
				ns.sendto(perm,addr)
			elif confirm == 'hashnotsame' or confirm == 'newfile':
				try:
					f = open(filename, "rb")
					byte = f.read(1024)
					#print byte
					while byte:
						#print byte
						ns.sendto(byte, addr)
						data, addr = ns.recvfrom(1024)
						print data
						if data != "recieved":
							break
						byte = f.read(1024)
					ns.sendto("done", addr)
					command = "stat --printf 'name: %n \tSize: %s bytes\t Timestamp:%z\t' " + filename
					result1 = os.popen(command).read()
					perm = str(oct(os.stat(filename)[ST_MODE])[-3:])
					#print perm
					result = result1 + '\t' + perm
					#print result
					s.send(result)
				except:
					print "Bad Connection Error"
					return
	if protocol == "TCP":
		#calculate hash and send to client through socket
		file_hash = os.popen('md5sum "' + filename + '"').read().split()[0] # command for calculating md5sum
		s.send(file_hash)
		confirm = s.recv(1024)
		if confirm == 'hashsame':
			perm1 = str(oct(os.stat(filename)[ST_MODE])[-3:])
			#print perm1
			perm = 'nodatasent ' + perm1
			s.send(perm)
		elif confirm == 'hashnotsame' or confirm == 'newfile':
			try:
				fil = open(filename, "rb")
				byte_wise = fil.read(1024)
				while byte_wise:
					s.send(byte_wise)
					if s.recv(1024) != "recieved":
						break
					byte_wise = fil.read(1024)
				s.send("done")
				command = "stat --printf 'name: %n \tSize: %s bytes\t Timestamp:%z\t' " + filename
				result1 = os.popen(command).read()
				perm = str(oct(os.stat(filename)[ST_MODE])[-3:])
				#print perm
				result = result1 + '\t' + perm
				#print result
				s.send(result)
				print 'Done'
			except:
				print "Error in connection"
				return
	if protocol!='UDP' and protocol!='TCP':
		print 'Wrong arguments'
def sendhashes(s):
	cmd = 'ls'
	result = os.popen(cmd).read()
	files = result.split()
	i=0
	while i<len(files):
		fil = '"' + files[i] + '"'
		cmd = "stat --printf '%F' " + fil
		Type = os.popen(cmd).read()
		#Type = Type1.split(':')
		print Type
		if Type == 'regular file':
			file_hash = os.popen('md5sum "' + files[i] + '"').read().split()[0] # command for calculating md5sum
			totstr = file_hash + '\t' + files[i]
			s.send(totstr)
		elif Type == 'directory':
			file_hash = '-1'
			s.send(file_hash + '\t' + files[i])
		data = s.recv(1024)
		i = i+1
	s.send('done')

def senddirectory(s,args):
	div = args.split()
	directory = " ".join(div[2:])
	print directory
	if (os.popen('ls "' + directory + '"').read().split('\n')[0] == ""):
		print 'no such directory'
		return
	hash_value = -1
	cmd = 'cd ' + directory
	os.system(cmd)
	command = 'ls'
	files = os.popen(command).read()
	i=0
	while i<len(files):
		args = 'download TCP' + files[i]
		fil = '"' + files[i] + '"'
		cmd = "stat --printf 'Type: %F\t' " + fil
		Type = os.popen(cmd).read()
		if Type == 'regular file':
			sendfile(s,args,files[i])
		elif Type == 'directory':
			senddirectory(s,args)
		i = i+1

	#data = s.recv(1024)
	#print data
	#if data == 'send_status':
	#	s.send(result)
	
	#	print "Done"

s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
host = "0.0.0.0"
port = input("Port: ") # Enter the port number
#print port
#port = 6001
try:
	s.bind((host, port))
except:
	print "Socket creation Error"
	exit(0)
s.listen(5)

sharedfolder1 = raw_input("Enter full path of the folder to share with 2: ")

if not os.path.exists(sharedfolder1):
	print "No Such Folder"
	exit(0)
elif not os.access(sharedfolder1, os.R_OK):
	print "No Privilleges"
	exit(0)
else:
	os.chdir(sharedfolder1)
print 'Directory changed'

#try:
#    log = open("server_log.log", "a+")
#except:
#    print "Cannot Open Log file"
#    exit(0)
print 'Server is up and listening....'

while True:
	try:
		conn, addr = s.accept()
	except:
		s.close()
	print 'Got connection from', addr
	
	while True:
		#data = conn.recv(1024)
		#print data
		#conn.send('modeset')
		#if data == '1':
		try:
			#print 'conn'
			data = conn.recv(1024)
			#print 'conn cont'
		except:
			conn.close()
			print "connection closed to client"
			break
		div = data.split()
		#print data
			#print div[0]
			#print div[1]
			#print div[2]
		if len(div) == 0 or div[0] == "over":
			conn.close()
			print "Connection closed to client"
			break
		elif div[0] == 'change' and div[1] == 'directory':
			print 'entered'
			directory = div[2]
			#cmd = 'cd ' + directory
			print directory
			os.chdir(directory)
			cmd = 'pwd'
			cwd = os.popen(cmd).read()
			print cwd
			conn.send('changed')
		elif div[0] == 'send' and div[1] == 'hashes':
			print 'send all hashes'
			sendhashes(conn)
		elif div[0] == 'download':
			#print 'download entered'
			#filename = " ".join(div[2:])
			#fil = '"' + filename + '"'
			#cmd = "stat --printf 'Type: %F\t' " + fil
			#Type = os.popen(cmd).read()
			#if Type == 'regular file':
			sendfile(conn, data)
			#elif Type == 'directory':
			#	senddirectory(conn,data)
		elif div[0] == 'hash':
			if div[1] == 'verify':
				filename = " ".join(div[2:])
				send_filehash(conn,filename)
			elif div[1] == 'checkall':
				send_allhash(conn,'cksum')
		elif div[0] == 'index':
			if div[1] == 'longlist':
				longlist(conn,data)	
			elif div[1] == 'shortlist' and len(div) == 4:
				#print 'ent'
				shortlist(conn,data)
			elif div[1] == 'regex' and len(div) == 3:
				regex(conn,data)
		else:
			conn.send("Invalid Command")
			conn.send("done")
	conn.close()





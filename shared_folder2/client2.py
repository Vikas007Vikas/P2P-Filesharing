import socket
import os
import hashlib
import time
import platform
from datetime import datetime
import re
import json
from stat import *
def hash_value_func(filename):
	fil = open(filename, 'rb') # rb indicate - open a file for reading
	hashval = hashlib.md5(fil.read()).hexdigest()
	return hashval
def hash_verify(s,filename):
	#print filename
	recv_hash = s.recv(1024)
	return recv_hash
def hash_checkall(s):
	while True:
		data = s.recv(1024)
		#s.send("gotit")
		filename = s.recv(1024)
		#s.send("gotfile")
		hash_value = hash_verify(s,filename)
		if data == 'done':
			break
		print 'last modified time:' + data + '\t' + 'hash_value:' + hash_value + '\t' + filename
def directorydownload(s,protocol,directory):
	if os.path.exists(directory):
		#cmd = 'cd ' + directory
		#print 'made'
		os.chdir(directory)
	else:
		#print 'make'
		#cmd = 'mkdir ' + directory
		os.mkdir(directory)
		os.chdir(directory)
	s.send('change directory ' + directory)
	data = s.recv(1024)
	#print data
	if data != 'changed':
		print data
	s.send('send hashes')
	file_array = []
	hash_array = []
	while True:
		data = s.recv(1024)
		#print data
		data1 = data.split('\t')
		if data == 'done':
			break
		s.send('recieved')
		file_array.append(data1[1])
		hash_array.append(data1[0])
	#print file_array
	#print hash_array
	i=0
	while i<len(file_array):
		#print 'entered'
		hash_value = hash_array[i]
		#print hash_value
		if hash_value == '-1':
			directorydownload(s,protocol,file_array[i])
		else:
			args = 'download ' + protocol + ' ' + file_array[i]
			result = filedownload(s,args,file_array[i],protocol)
			#print result
			fil = open(file_array[i], 'rb') # rb indicate - open a file for reading
			sent_hash = hashlib.md5(fil.read()).hexdigest()
			result1 = result.split()
			#print result1
			if result1[0] == 'nodatasent':
				command = 'chmod ' + result1[1] + ' ' + file_array[i]
				#print command
				os.system(command)
				print(file_array[i] +':file already existing in the folder and uptodate')
			else:
				if result != sent_hash:
					print(file_array[i]+':download failed hash not same')
				else:
					#s.send('send_status')
					data = s.recv(1024)
					spl = data.split('\t')
					perm = spl[4]
					#print('permissions:' + perm)
					command = 'chmod ' +perm + ' ' + file_array[i]
					#print command
					os.system(command)
					permissions = str(oct(os.stat(file_array[i])[ST_MODE])[-3:])
					#print permissions
					#print data
					print('hash:' + result + '\t' + data)
					#print 'Downloading completed successfully'
					print(file_array[i]+':file downloaded successfully')
		i = i+1
	os.chdir('..')
	s.send('change directory ' + '..')
	data = s.recv(1024)
	#print data
	if data != 'changed':
		print data

def filedownload(s,args , filename , protocol):
	#print protocol
	flag = 2
	poi = 0
	s.send(args)
	data = s.recv(1024)
	#print data
	if data != 'recieved':
		#print 'abc'
		print data
	if protocol!='UDP' and protocol!='TCP':
		print 'wrong protocol argument'
		return
	#if protocol == 'UDP':
		#has to create a new socket ns with SOCK_DGRAM
	#	new_port = int(s.recv(1024))
	#	ns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#	ns.close()
	if protocol == 'UDP':
		new_port = (s.recv(1024))
		#print "ssss"+new_port
		ns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		addr = (host,int(new_port))
		ns.sendto("recieved", addr)
		recv_hash1 = ns.recvfrom(1024)
		#print recv_hash1
		#recv_hash2 = recv_hash1.split()
		recv_hash = recv_hash1[0]
		#print recv_hash 
		cmd = "ls"
		#os.system(cmd)
		result = os.popen(cmd).read()
		files = result.split()
		#print files
		num = len(files)
		#print num
		i=0
		while i<num:
			if(files[i] == filename):
				poi = 1
				hash_value_in = hash_value_func(files[i])
				hash_value_orig = recv_hash
				if hash_value_in == hash_value_orig:
					flag = 1
					#print 'hashsame'
					ns.sendto('hashsame',addr)
				elif hash_value_in != hash_value_orig:
					flag = 0
					#print 'hashnotsame'
					ns.sendto('hashnotsame',addr)
					#print 'hashnotsame'
				break
			i = i+1
		if poi == 0:
			flag = 2
			ns.sendto('newfile',addr)
		if flag == 0:
			cmd1 = "rm " + filename
			os.system(cmd1)
			command = "touch " + filename
			#print command
			os.system(command)
			try:
				f = open(filename,'wb+')
			except:
				print "no space"
				return
			while True:
				data, addr = ns.recvfrom(1024)
				if data == 'done':
					break
				f.write(data)
				ns.sendto("recieved",addr)
			return recv_hash
		elif flag == 1:
			data1 = ns.recvfrom(1024)
			#print data1
			data = data1[0]
			#print data
			return data
		elif flag == 2:
			try:
				f = open(filename,'wb+')
			except:
				print "no space"
				return
			while True:
				data, addr = ns.recvfrom(1024)
				if data == 'done':
					break
				f.write(data)
				ns.sendto("recieved",addr)
			return recv_hash
		f.close()
		ncs.close()

	if protocol == 'TCP':
		#can use the old socket s
		recv_hash = s.recv(1024)
		cmd = "ls"
		#os.system(cmd)
		result = os.popen(cmd).read()
		files = result.split()
		#print files
		num = len(files)
		#print num
		i=0
		while i<num:
			if(files[i] == filename):
				poi = 1
				hash_value_in = hash_value_func(files[i])
				hash_value_orig = recv_hash
				if hash_value_in == hash_value_orig:
					flag = 1
					s.send('hashsame')
				elif hash_value_in != hash_value_orig:
					flag = 0
					s.send('hashnotsame')
				break
			i = i+1
		if poi == 0:
			flag = 2
			s.send('newfile')
		if flag == 0:
			cmd1 = "rm " + filename
			os.system(cmd1)
			command = "touch " + filename
			#print command
			os.system(command)
			try:
				fil = open(filename,'wb+') # wb+ indicate - create a file which can be updated
			except:
				print "cannot open the file"
				return
			while True:
				data = s.recv(1024)
				if data == 'done':
					break
				fil.write(data)
				s.send('recieved')
				fil.close()
				#s.close()
			return recv_hash
		elif flag == 1:
			#while True:
			#	data = s.recv(1024)
			#	if data == 'done':
			#		break
			#	s.send('recieved')
			data = s.recv(1024)
			#print data
			return data
		elif flag == 2:
			#print '2'
			try:
				fil = open(filename,'wb+') # wb+ indicate - create a file which can be updated
			except:
				print "cannot open the file"
				return
			while True:
				#print 'transfer'
				data = s.recv(1024)
				if data == 'done':
					break
				fil.write(data)
				s.send('recieved')
				fil.close()
				#s.close()
			return recv_hash

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = input("enter port number: ") # Enter the port of server2 - folder2 server
host = raw_input("Enter Host-ip: ") 
sharedfolder2 = raw_input("Shared Folder2: ") # Full path the folder you wish to share 
#port = 6000
#host = '127.0.0.1'
#sharedfolder2 = 'folder2'
if not os.path.exists(sharedfolder2):
	print "No Such Folder"
	exit(0)
elif not os.access(sharedfolder2, os.W_OK):
	print "No Privilleges"
	exit(0)
else:
	os.chdir(sharedfolder2)
#try:
#    log = open("client_log.log", "a+")
#except:
#    print "Cannot Open Log file"
#    exit(0)
try: 
	s.connect((host,port))
except:
	print 'No available server with that Host-ip'
	s.close()
	exit(0)
cnt = 0
print 'Connection established'
mode = 1
strt_flag = input("Enter the mode sync(1) prompt(0) \nprompt> ")
while True:
	cnt += 1
	#curr_time = time.time()
	#curr_time1 = curr_time
	#while curr_time1 - curr_time<=5:
	#	strt_flag = 1
	#	curr_time1 = time.time()
	#mode = raw_input("prompt> ")
	#s.send(mode)
	#data = s.recv(1024)
	#if data != 'modeset':
	#	print data
	if strt_flag == 1 :
		#strt_flag = 0
		args = 'hash checkall'
		#s.send('send hashes')
		#data = s.recv(1024)
		#print data
		#if data != 'recieved':
		#	print data
		#hash_array = []
		#name_array = []
		#while True:
		#	data = s.recv(1024)
		#	if data == 'done':
		#		break
		#	s.send('recieved')
		#	val = data.split('\t')
		#	hash_array.append(val[1])
		#	name_array.append(val[2])
		#print hash_array
		#print name_array

		s.send('send hashes')
		file_array = []
		hash_array = []
		while True:
			data = s.recv(1024)
			#print data
			data1 = data.split('\t')
			if data == 'done':
				break
			s.send('recieved')
			file_array.append(data1[1])
			hash_array.append(data1[0])
		i= 0
		while i<len(file_array):
			x = hash_array[i]
			if x == '-1':
				directorydownload(s,'TCP',file_array[i])
			else:
				args = 'download TCP ' + file_array[i] 
				result = filedownload(s,args,file_array[i],'TCP')
				#print result
				hash_val = hash_value_func(file_array[i])
				result1 = result.split()
				if result1[0] == 'nodatasent':
					print( file_array[i] + ':file already existing in the folder and uptodate')
				else:
					if result1[0]!=hash_val:
						print(file_array[i] + ':download failed hash not same')
					elif result1[0]==hash_val:
						data = s.recv(1024)
						#print('hash:' + result + '\t' + data)
						#print 'Downloading completed successfully'
						print(file_array[i] + ':file downloaded successfully')
			i = i+1
		print 'sync done'
		strt_flag = 0
		#s.send('over')					
		continue


	elif strt_flag == 0:
		args = raw_input("prompt> ")
		div = args.split()
		#print div[0]
		#print div[1]
		#print div[2]
		if len(div)==0 or div[0]=='close':
			s.send(args)
			print 'no command entered'
			s.close()
		elif div[0]=='download':
			#print 'ab'
			s.send('send hashes')
			file_array = []
			hash_array = []
			while True:
				data = s.recv(1024)
				#print data
				data1 = data.split('\t')
				if data == 'done':
					break
				s.send('recieved')
				file_array.append(data1[1])
				hash_array.append(data1[0])
			#print file_array
			#print hash_array


			filename = " ".join(div[2:])
			#s.send('send')
			i=0
			while i<len(file_array):
				if filename == file_array[i]:
					hash_value = hash_array[i]
					if hash_value == '-1':
						#print 'ent dir'
						protocol = div[1]
						directorydownload(s,protocol,file_array[i])
					else:
						result = filedownload(s,args, filename, div[1]) #div[1] refers to UDP/TCP and div[2] refers to filename to be downloaded
						#print('result=%s', (result))
						# now we will check whether the recieved file hash value is same as the sent file hash value
						fil = open(filename, 'rb') # rb indicate - open a file for reading
						sent_hash = hashlib.md5(fil.read()).hexdigest()
						result1 = result.split()
						#print result1
						if result1[0] == 'nodatasent':
							command = 'chmod ' + result1[1] + ' ' + filename
							#print command
							os.system(command)
							print 'file already existing in the folder and uptodate'
						else:
							if result != sent_hash:
								print 'download failed hash not same'
							else:
								#s.send('send_status')
								data = s.recv(1024)
								#print data
								spl = data.split('\t')
								perm = spl[4]
								#print('permissions:' + perm)
								command = 'chmod ' +perm + ' ' + filename
								#print command
								os.system(command)
								permissions = str(oct(os.stat(filename)[ST_MODE])[-3:])
								#print permissions
								#print data
								print('hash:' + result + '\t' + data)
								#print 'Downloading completed successfully'
								print 'file downloaded successfully'
					break
				i = i+1

		elif div[0]=='hash':
			if div[1] == 'verify':
				filename = " ".join(div[2:])
				#print filename
				s.send(args)
				data = s.recv(1024)
				#print data
				if data != 'recieved':
					print data
				result = hash_verify(s,filename)
				s.send("recieved")
				#timestamp = s.recv(1024)
				print('hash:' + result )
				#print('last modified time:' +timestamp)
			elif div[1] == 'checkall':
				s.send(args)
				data = s.recv(1024)
				#print data
				if data != 'recieved':
					print data
				while True:
					data = s.recv(1024)
					if data == 'done':
						break
					s.send('recieving')
					print data
		elif div[0] == 'index':
			#print 'entered'
			if div[1] == 'longlist':
				#print 'entered 2'
				s.send(args)
				data = s.recv(1024)
				if data != 'recieved':
					print data
				while True:
					data = s.recv(1024)
					if data == 'done':
						break
					s.send('recieving')
					print data
			elif div[1] == 'shortlist' and len(div) == 4:
				#print 'ent'
				s.send(args)
				data = s.recv(1024)
				if data != 'recieved':
					print data
				while True:
					data = s.recv(1024)
					if data == 'done':
						break
					s.send('recieving')
					print data
			elif div[1] == 'regex' and len(div) == 3:
				s.send(args)
				data = s.recv(1024)
				if data != 'recieved':
					print data
				while True:
					data = s.recv(1024)
					if data == 'done':
						break
					s.send('recieving')
					print data
			else:
				print 'input format wrong'


s.close()
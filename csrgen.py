#!/usr/bin/python3
##############################################
#Brian Rawlins - CSID -  12/18/2017
##############################################
# CSR Generator Tool         				 #
##############################################

import os
import time


PATH = './csr'
#Create constants for menu
GEN_CSR =	'1'
SAN_CSR =	'2'
EXIT_SEL =	'3'

#Define the main funtion
def main():

	#Print the banner
	banner()

	#prime the selection variable
	selection = '0'
	#while loop for menu
	while selection != EXIT_SEL:
		#call menu_display()
		menuDisplay()
		#Get the users menu selection
		selection = str(input('Enter your selection: '))
		#Genetate a sha256 RSA CSR
		if selection == GEN_CSR:
			x1 = GenCsr()
			user_input = []
			correct = False
			while correct != True:
				user_input = list(getUserInput())
				print()
				print('Domain Name:	', user_input[0])
				print('Organization:	', user_input[1])
				print('Department:	', user_input[2])
				print('Email:		', user_input[6])
				print('City:		', user_input[3])
				print('State:		', user_input[4])
				print('Country:	', user_input[5])
				print()
				print(' Is the information correct? (Y/N)', end='')
				proceed = input().upper()
				print()
				if proceed == 'Y':
					correct = True
				else:
					correct = False
			#Generate the csr/key
			x1.type_RSA(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4], user_input[5], user_input[6])

		#GEnerate a sha256 SAN CSR
		elif selection == SAN_CSR:
			x1 = GenCsr()
			user_input = []
			san_list = []
			correct = False
			while correct != True:
				user_input = list(getUserInput())
				add_sans = 'Y'
				while add_sans == 'Y':
					san_names = input('SAN Name: ')
					san_list.append(san_names)
					print('Enter another alt name? (Y/N)', end='')
					add_sans = input().upper()
				user_input.append(san_list)
				print()
				print('Domain Name:	', user_input[0])
				print('Organization:	', user_input[1])
				print('Department:	', user_input[2])
				print('Email:	', user_input[6])
				print('City:		', user_input[3])
				print('State:		', user_input[4])
				print('Country:	', user_input[5])
				print('SAN Name(s):	', user_input[7])
				print()
				print(' Is the information correct? (Y/N)', end='')
				proceed = input().upper()
				print()
				if proceed == 'Y':
					correct = True
				else:
					correct = False
			#Generate the csr/key
			x1.type_RSA(user_input[0], user_input[1], user_input[2], user_input[3], user_input[4], user_input[5], user_input[6], user_input[7])
		#Quit the program
		elif selection == EXIT_SEL:
			print()
		else:
			print('Error: invalid selection')


#Define the banner function
def banner():

	#Print the Program banner
	printThree()
	print('#' * 40)
	print('#         CSID CSR Generator Tool   #')
	print('#' * 40)
	printThree()

def printThree():
	print()
	print()


#Define the menuDisplay function
def menuDisplay():
	print()
	print('1) Generate Single Domain or Wildcard CSR (sha256)')
	print('2) Generate SAN(subject alternative name) CSR (sha256)')
	print('3) Quit')
	print()

def getUserInput():
	print()
	CN = input('Domain Name: ')
	O = input ('Organization: ')
	OU = input('Department: ')
	email = input('Email Address: ')
	L = input('City: ')
	ST = input('State: ')
	C = input('Country[US]: ').upper()
	if len(C) > 2 or len(C) < 2:
		while len(C) > 2 or len(C) < 2:
			print('Country must be 2 characters in length.')
			C = input('Country[US]: ').upper()
	return(CN, O, OU, L, ST, C, email)



class GenCsr(object):

	def __init__(self):
		fpath = PATH
		#if not os.path.exists(fpath):
		#	os.mkdir(fpath)


	def _clean_old_files(self):
		for file in [self.csr_path,
					self.conf_path,
					self.pvtkey_path, ]:
			if(os.path.exists(file)):
				os.remove(file)

	def _gen_openssl_conf(self):
		f=open(self.conf_path,'w')
		f.write('[ req ]' + '\n' + 'default_bits= ' + self.Key_Size +
'''
prompt = no
encrypt_key = no
distinguished_name = dn
default_md = ''' + self.hash_alg + "\n")

		sanincsrFlag = None
		if self.SanInCSR is not None and self.SanInCSR != []:
			f.write("req_extensions = v3_req\n")
			sanincsrFlag = True

		f.write(
			"[ dn ]\n" +
			"CN = " + self.CN + "\n" +
			"emailAddress =" + self.Email + "\n" +
			"O = "  + self.O + "\n" +
			"L = "  + self.L + "\n" +
			"ST = " + self.ST + "\n" +
			"C = "  + self.C + "\n" +
			"OU= "+ self.OU + "\n"

 		)

		if sanincsrFlag :
			f.write('[ v3_req ]\n')
			f.write('subjectAltName = @alt_names\n')
			f.write('[ alt_names ]\n')
			count = 1
			for san in self.SanInCSR :
				f.write('\n' + 'DNS.' + str(count) + ' = '  + san )
				count += 1

		f.close()

	def _gen_csr(self):
		fpath = './'
		self.csr = None
		self.csr_path = fpath+self.CN+'.csr'
		self.pvtkey_path = fpath+self.CN+'.key'
		self.conf_path = fpath+self.CN+'.conf.txt'
		self._clean_old_files()
		self._gen_openssl_conf()
		#Generate Private Key Generating OpenSSL Command
		#rsaPvtKeyGenCommand = "openssl genrsa -out " + self.pvtkey_path + " " + self.Key_Size
		#os.popen(rsaPvtKeyGenCommand)
		#Generate Private Key Generating OpenSSL Command
		csrGenCommand = "openssl req -new -sha256 -newkey rsa:2048 -nodes -out "+self.csr_path+" -keyout "+self.pvtkey_path+" -config "+self.conf_path #-subj /C="+self.C+"/ST="+self.ST+"/L="+self.L+"/O="+self.O+"/OU="+self.OU+"/CN="+self.CN
#		csrGenCommand = "openssl req -new -sha256 -newkey rsa:4096 -nodes -out "+self.csr_path+" -keyout "+self.pvtkey_path+" -config "+self.conf_path #-subj /C="+self.C+"/ST="+self.ST+"/L="+self.L+"/O="+self.O+"/OU="+self.OU+"/CN="+self.CN
		# Generate CSR
		#csrGenCommand = "openssl req -new -key " + self.pvtkey_path + " -out " + self.csr_path + " -config " + self.conf_path
		print(csrGenCommand)
		os.popen(csrGenCommand)
		time.sleep(5)
		print('#' * 80)
		print('csr saved in file : %s' %os.path.abspath(self.csr_path))
		print('private key saved in file : %s' %os.path.abspath(self.pvtkey_path))
		print('#' * 80)

		if os.path.exists(self.csr_path):
			print('Here is the CSR info to send to the CA')
			printThree()
			f = open(self.csr_path,'r')
			self.csr = f.read()
			print(self.csr)
			return True
		else:
			print('csr not created ................')
			return False

	def get_csr(self,CN,O,OU,L,ST,C,email,SanInCSR=[],keysize=2048,hash_alg='sha256',Signing_Algorithm='RSA'):
#	def get_csr(self,CN,O,OU,L,ST,C,email,SanInCSR=[],keysize=4096,hash_alg='sha256',Signing_Algorithm='RSA'):
		self.CN = CN
		self.SanInCSR = SanInCSR
		self.O = O
		self.OU = OU
		self.L = L
		self.ST = ST
		self.C = C
		self.Email = email
		self.Sig_Alg  = Signing_Algorithm
		self.Key_Size = str(keysize)
		self.hash_alg = hash_alg
		self._gen_csr()
        #self.gen_loadrunner_csr()
		return self.csr

	def type_RSA(self,CN,O,OU,L,ST,C,email,SanInCSR=[],keysize=2048,hash_alg='sha256'):
#	def type_RSA(self,CN,O,OU,L,ST,C,email,SanInCSR=[],keysize=4096,hash_alg='sha256'):
		print('#' * 40)
		print('System call to generate a RSA csr')
		print('#' * 40)
		return self.get_csr(CN,O,OU,L,ST,C,email,SanInCSR,keysize,hash_alg,'RSA')


#call main
main()



#End Of Program

from flask import Flask

from flask import render_template
from flask_httpauth import HTTPBasicAuth
#from flask_restful import Api, Resource

import os
import os.path
import signal

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import subprocess

app = Flask(__name__)
auth=HTTPBasicAuth()

process=None

userRegistered=False
testnetAppRunning=False
mainnetAppRunning=False

users = {}

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
	return render_template("index.html")
	return 'XLM Environment Monitor api is running. View documentation here; '

#Also needs work.
@app.route('/register/<username>/<password>')
def register(username, password):
	global users, userRegistered
	if userRegistered==True:
		return 'Admin already registered.'
	else:
		users={username:password}
		userRegistered=True
		return 'user registered! welcome ' + username

#Needs a LOT of work.
@auth.verify_password
def verify_password(username, password):
	global users
	if username in users:
		return True
	else:
		return False


@app.route('/run/testnet/<int:interval>')
@auth.login_required
def testnetService(interval):
	global testnetAppRunning, mainnetAppRunning, process
	if testnetAppRunning==True:
        	return 'Testnet App already running.'
	elif mainnetAppRunning==True:
		return 'Mainnet App already running. Please terminate before retrying.'
	else:
		#request to set up the new address with free testnet XLM
		keys=genKeypair(True)
		testnetXlmUrl='https://friendbot.stellar.org'
		response=requests.get(testnetXlmUrl, params={'addr':keys.public_key})

		runApp(interval)

		with open('testnetrunning.txt') as f:
			f.write(str(interval))

		testnetAppRunning=True
		return 'App running on testnet on ' + "<a href=\""+getExplorerURL(True,keys.public_key)+"\">" + keys.public_key+"</a>"

#Returns the pubkey that the app is running on
@app.route('/get/pubkey')
def getPubKey():

	keyFile=open("keys.txt", "r")
	text = keyFile.read()
	keyFile.close()

	processedText=[x.strip() for x in text.split(',')]

	return processedText[0] + ": " + processedText[1]


@app.route('/run/mainnet/<int:interval>')
@auth.login_required
def mainnetService(interval):
	global testnetAppRunning, mainnetAppRunning,process
	if testnetAppRunning==True:
		return 'Testnet App already running.'
	elif mainnetAppRunning==True:
		return 'mainnet app is already running'
	else:
		#Check Inputs
		if interval <= 1:
			return 'interval can not be less than 2 seconds'

		keys=genKeypair(False)

		runApp(interval)

		mainnetAppRunning=True
		with open("mainrunning.txt", "w") as f:
			f.write(str(interval))

		return 'running app on mainnet. Please send XLM to: ' + keys.public_key

#delete all files and halt all processes (need to add halt process functionality.)
@app.route('/reset')
@auth.login_required
def reset():
	#os.system("rm nohup.txt")
	#os.system("rm pubkey.txt")
	global users, mainnetRunning, testnetRunning, userRegistered, process
	users = {}
	mainnetRunning=False
	testnetRunning=False
	userRegistered=False

	process.terminate()
	os.kill(process.pid, signal.SIGINT)

	return "users deleted, processes stopped."

#testnet must be a boolean value. True for testnet, False for mainnet
def genKeypair( testnet ):

	if KEY_GEN is not True:
		keypair = Keypair.random()

		if testnet is True:
			str="TESTNET,"
		else:
			str="MAINNET,"

		str+=keypair.public_key
		str+=","
		str+=keypair.secret

		f=open("keys.txt", "w")
		f.write(str)
		f.close()
		return keypair

	else:
		with open("keys.txt") as f:
			keydata=f.read()
			keydata=[x.strip() for x in keydata.split(',')]
			return Keypair.from_secret(keydata[2])

#needs testing. i.e. if status.txt doesn't exist, what happens?
#need to add text saying what's running too
@app.route()('/get/status')
def getStatus():
	with open('status.txt', 'r') as f:
		ret=f.read()
	return ret

#returns url to stellar expert explorer.
def getExplorerURL( isTestnet, pubkey):

	link="https://stellar.expert/explorer/"
	if isTestnet is True:
		link+="testnet/"
	else:
		link+="public/"

	link+="account/" + pubkey


	return link

def runApp(interval):
	global process
	process=subprocess.Popen(["python3", "read.py", str(interval)])



if os.path.isfile('keys.txt') is True:
	KEY_GEN=True
else:
	KEY_GEN=False

if os.path.isfile('mainrunning.txt') is True:
	#read the file and send data to
	interval=None
	with open('mainrunning.txt') as f:
		interval=f.read()
	runApp(interval)
elif os.path.isfile('testnetrunning.txt') is True:
	interval=None
	with open('testnetrunning.txt') as f:
		interval=f.read()
	runApp(interval)


if __name__ == '__main__':
	app.run(port=5000, host='0.0.0.0', debug=True)

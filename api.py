from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource
import os

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests

app = Flask(__name__)
auth=HTTPBasicAuth()

userRegistered=False
testnetAppRunning=False
mainnetAppRunning=False

users = {}

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
	return 'XLM Environment Monitor is running. View documentation here; '

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


@app.route('/run/testnet')
@auth.login_required
def testnetService():
	global testnetAppRunning, mainnetAppRunning
	if testnetAppRunning==True:
        	return 'Testnet App already running.'
	elif mainnetAppRunning==True:
		return 'Mainnet App already running. Please terminate before retrying.'
	else:
		#request to set up the new address with free testnet XLM
		keys=genKeypair(True)
		testnetXlmUrl='https://friendbot.stellar.org'
		response=requests.get(testnetXlmUrl, params={'addr':keys.public_key})

		#os.system('nohup python3 ./repTnTx.py &')
		os.system('nohup python3 ./run.py &')
		testnetAppRunning=True
		return 'App running on testnet on ' + keys.public_key + "<p>"+getExplorerURL(True,keys.public_key)+"</p>"

#Returns the pubkey that the app is running on
@app.route('/get/pubkey')
def getPubKey():

	keyFile=open("keys.txt", "r")
	text = keyFile.read()
	keyFile.close()

	processedText=[x.strip() for x in text.split(',')]

	return processedText[0] + ": " + processedText[1]


@app.route('/run/mainnet/<int:temp>/<int:humid>/<int:interval>')
@auth.login_required
def mainnetService(temp, humid, interval):
	global testnetAppRunning, mainnetAppRunning
	if testnetAppRunning==True:
		return 'Testnet App already running.'
	elif mainnetAppRunning==True:
		return 'mainnet app is already running'
	else:
		#Check Inputs
		if temp < 0 or temp >= 2:
			return 'temp variable out of bounds. Should be 0 or 1'
		if humid < 0 or humid >= 2:
			return 'humid variable out of bounds. Should be 0 or 1'
		if interval <= 1:
			return 'interval can not be less than 2 seconds'

		keys=genKeypair(False)
		os.system('nohup python3 ./run.py &')
		mainnetAppRunning=True

		return 'running app on mainnet. Please send XLM to: ' + keys.public_key

#delete all files and halt all processes (need to add halt process functionality.)
@app.route('/reset')
@auth.login_required
def reset():
	os.system("rm nohup.txt")
	os.system("rm pubkey.txt")
	global users, mainnetRunning, testnetRunning, userRegistered
	users = {}
	mainnetRunning=False
	testnetRunning=False
	userRegistered=False


#testnet must be a boolean value. True for testnet, False for mainnet
def genKeypair( testnet ):
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

#returns url to stellar expert explorer.
def getExplorerURL( isTestnet, pubkey):

	link="https://stellar.expert/explorer/"
	if isTestnet is True:
		link+="testnet/"
	else:
		link+="public/"

	link+="account/" + pubkey


	return link




if __name__ == '__main__':
	app.run(port=5000, host='0.0.0.0', debug=True)


from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth

import os
import os.path
import os.remove
import signal

from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import subprocess

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

import json

app = Flask(__name__)
auth=HTTPBasicAuth()

process=None
userRegistered=False
KEY_GEN=False
testnetAppRunning=False
mainnetAppRunning=False

def resetUserDB():
	global userRegistered
	userdb=sqlite3.connect("users.db")
	curs=userdb.cursor()

	curs.execute('''DROP TABLE IF EXISTS users''')
	userdb.commit()

	curs.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, pwhash TEXT)''')
	userdb.commit()
	userdb.close()
	userRegistered=False

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/register')
def register():
	global userRegistered
	if userRegistered==True:
		return 'Admin already registered.'
	else:
		return render_template("register.html")

@app.route('/register_submit', methods=['POST'])
def register_submission():
	global userRegistered
	if userRegistered == True:
		return "err user already registered. Please /reset to register the new admin."
	add_user_to_db(request.form["username"], request.form["password"])
	return "Admin: " + request.form["username"] + " registered successfully."

def add_user_to_db(uname, pword):
	try:
		resetUserDB()
		pwhash=generate_password_hash(pword)
		vals=[uname, pwhash]
		userdb=sqlite3.connect("users.db")
		curs=userdb.cursor()
		curs.execute("INSERT INTO users VALUES(NULL, ?, ?)", vals)
		userdb.commit()
		userdb.close()
		return True
	except Exception as e:
		print(e)
		return False

@auth.verify_password
def verify_password(username, password):
	userdb=sqlite3.connect("users.db")
	curs=userdb.cursor()
	curs.execute('SELECT * FROM users WHERE username=?', [username])
	res=curs.fetchone()
	userdb.close()

	if res is not None:
		if res[1] == username and generate_password_hash( res[2] ):
			return True
	return False



@app.route('/run')
@auth.login_required
def send_run_app_form():
	if mainnetAppRunning==True or testnetAppRunning==True:
		return 'Application already running'
	else:
		return render_template("run_form.html")


@app.route('/run_submit', methods=['POST'])
@auth.login_required
def run_submission():
	global mainnetAppRunning, testnetAppRunning
	if mainnetAppRunning == True or testnetAppRunning == True:
		return "Application already running."

	if request.form["NETWORK"] == "MAINNET":
		return mainnetService(int(request.form["INTERVAL"]))
	elif request.form["TESTNET"] == "TESTNET":
		return testnetService(int(request.form["INTERVAL"]))


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

		with open('testnetrunning.txt', "w") as f:
			f.write(str(interval))

		testnetAppRunning=True
		return 'App running on testnet on ' + "<a href=\""+getExplorerURL(True,keys.public_key)+"\">" + keys.public_key+"</a>"


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

		return 'running app on mainnet. Please send XLM to: ' + "<a href=\""+getExplorerURL(False ,keys.public_key)+"\">" + keys.public_key+"</a>"



#Returns the pubkey and network that the app is running on
@app.route('/get/pubkey')
def getPubKey():
	if os.path.isfile('keys.txt') is True:
		keyFile=open("keys.txt", "r")
		text = keyFile.read()
		keyFile.close()
		processedText=[x.strip() for x in text.split(',')]
		return processedText[0] + ": " + processedText[1]
	else:
		return "Keypair has not yet been created."


#delete all files and halt all processes
@app.route('/reset')
@auth.login_required
def reset_page():
	return reset()



def reset():
	global mainnetAppRunning, testnetAppRunning, userRegistered, process

	if mainnetAppRunning is True:
		os.remove('mainrunning.txt')
		mainnetAppRunning=False

	if testnetAppRunning is True:
		os.remove('testnetrunning.txt')
		testnetAppRunning=False

	userRegistered=False
	resetUserDB()

	if process is not None:
		process.terminate()
		process.wait()
	#ALSO NEED TO DELETE/MOVE DB FILE.
	return "users deleted, processes stopped."

@app.route('/refund')
@auth.login_required
def refund():
	if os.path.isfile("keys.txt") is True:
		return render_template("refund_confirm.html")
	else:
		return "keys have not yet been created as the application has not been ran"
@app.route('/refund_confirm', methods=['POST'])
@auth.login_required
def refund_confirm():
	if request.form["CONFIRM"]=="YES":
		return issue_refund()
	elif request.form["CONFIRM"]=="NO":
		return "XLM withdrawal process cancelled."

def issue_refund():

	#reset()
	f=open("keys.txt", "r")
	keytext=f.read()
	keydata=[x.strip() for x in keytext.split(',')]

	if keydata[0] == "TESTNET":
		reset()
		#DELETE KEYS.TXT
		return "Testnet funds have not been returned. Keys have been deleted"

	keypair=Keypair.from_secret(keydata[2])
	#get send address from first transaction
	url="https://horizon.stellar.org/accounts/"+keypair.public_key + "/transactions?limit=1"
	res=requests.get(url)
	res_as_json=json.loads(res.text)
	print(res_as_json)
	funds_origin=res_as_json["_embedded"]["records"][0]["source_account"]
	server=Server("https://horizon.stellar.org/")
	NET_PASS=Network.PUBLIC_NETWORK_PASSPHRASE
	account=server.load_account(keypair.public_key)
	txn=TransactionBuilder(
		source_account=account,
		network_passphrase=NET_PASS,
		base_fee=server.fetch_base_fee()
		).append_account_merge_op(
			destination=funds_origin
			).set_timeout(10000).build()

	txn.sign(keypair)
	reset()
	resetUserDB()
	os.remove("keys.txt")
	server.submit_transaction(txn)
	return "Account merged with source account."

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
@app.route('/get/status')
def getStatus():
	with open('status.txt', 'r') as f:
		return f.read()

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
	process=subprocess.Popen(["python3", "read.py", str(interval)], shell=False)

def carry_on_where_left_off():
	global mainnetAppRunning, testnetAppRunning, KEY_GEN
	if os.path.isfile('keys.txt') is True:
		KEY_GEN=True
	else:
		KEY_GEN=False

	if os.path.isfile('mainrunning.txt') is True:
		#read the file and send data to
		interval=None
		with open('mainrunning.txt') as f:
			interval=f.read()
		print("mainnet app was running.")
		runApp(interval)
		mainnetAppRunning=True
	elif os.path.isfile('testnetrunning.txt') is True:
		interval=None
		with open('testnetrunning.txt') as f:
			interval=f.read()
		print("testnet app was running.")
		runApp(interval)
		testnetAppRunning=True

def ensure_userdb_exists():
	if os.path.isfile('users.db') is not True:
		resetUserDB()
	else:
		try:
			userdb=sqlite3.connect("users.db")
			curs=userdb.cursor()
			curs.execute('SELECT * FROM users')
			row=curs.fetchone()
			if row is not None:
				userRegistered=True
			userdb.close()
		except:
			resetUserDB()

def startupcheck():
	print("running startupcheck")
	carry_on_where_left_off()
	ensure_userdb_exists()


if __name__ == '__main__':
	startupcheck()
	app.run(port=5000, host='0.0.0.0', debug=True, use_reloader=False)

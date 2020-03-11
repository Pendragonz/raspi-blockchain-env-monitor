from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource
import os

app = Flask(__name__)
auth=HTTPBasicAuth()
api=Api(app, prefix="/api/")

userRegistered=False
testnetAppRunning=False
mainnetAppRunning=False

users = {}

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
	return 'Hello World!'

@app.route('/register/<username>/<password>')
def register(username, password):
	global users, userRegistered
	if userRegistered==True:
		return 'Admin already registered.'
	else:
		users={username:password}
		userRegistered=True
		return 'user registered! welcome ' + username

@auth.verify_password
def verify_password(username, password):
	global users
	if username in users:
		return True
	else:
		return False


@app.route('/private')
@auth.login_required
def privvy():
	return 'welcome admin'


@app.route('/run/testnet')
@auth.login_required
def testnetService():
	global testnetAppRunning, mainnetAppRunning
	if testnetAppRunning==True:
        	return 'Testnet App already running.'
	elif mainnetAppRunning==True:
		return 'Mainnet App already running. Please terminate before retrying.'
	else:
		os.system('nohup python3 ./repTnTx.py &')
		testnetAppRunning=True
		return 'Ok Ill run that script in just a jiffy'

@app.route('/get/pubkey')
def getPubKey():
	f = open("pubkey.txt", "r")
	text = f.read()
	f.close()
	return text


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


		mainnetAppRunning=True
		return 'running app on mainnet'

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



if __name__ == '__main__':
	app.run(port=5000, host='0.0.0.0', debug=True)



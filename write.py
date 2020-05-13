from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import time
import sys
import getopt
import json
import os.path

import sqlite3

print("write.py started")

horizon = None
server = None
NET_PASS = None
keypair = None

#sets up global variables
def getKeysSettings():
	global horizon, server, NET_PASS, keypair

	#ensures keys.txt exists before continuing
	while os.path.isfile('keys.txt') is not True:
		writeStatus("Keys have not been created.")
		time.sleep(30)

	#Load keypair and settings from filesystem
	with open("keys.txt", "r") as f:
		keyData=f.read()

	#Process data and set up global variables
	listKeyData=[x.strip() for x in keyData.split(',')]

	if listKeyData[0] == "MAINNET":
		horizon="https://horizon.stellar.org/"
		server=Server(horizon)
		NET_PASS=Network.PUBLIC_NETWORK_PASSPHRASE
	else:
		horizon="https://horizon-testnet.stellar.org/"
		server=Server(horizon)
		NET_PASS=Network.TESTNET_NETWORK_PASSPHRASE

	keypair=Keypair.from_secret(listKeyData[2])

def writeStatus(txt):
	with open('status.txt', 'w') as f:
		f.write(txt)

#Checks if the Stellar account has been created and funded.
def accReady():
	res=requests.get(horizon+"accounts/"+keypair.public_key)
	if res.status_code == 200:
		try:
			res_as_json=json.loads(res.text)
			bal=res_as_json["balances"][0]['balance']
		except:
			print("error fetching balance.")
			return False
		else:
			if float(bal) >= 1.1:
				#everything is perfect, break out of loop
				balance_valid=True
				writeStatus("account valid, balance sufficient on launch;"+str(bal))
				return True
			else:
				writeStatus("balance="+str(bal)+". Please add more XLM")
				return False
	else:
		writeStatus("account not found/balance is 0")
		return False

#attempt to send a txn. If it fails, return false. If it succeeds, return true
def sendTXN(txn):
	try:
		response=server.submit_transaction(txn)
		print(response)
		return True
	except:
		return False
	return True

def getNextData():
	while True:
		#try to pull data
		try:
			dbconn=sqlite3.connect("envdata.db")
			try:
				c=dbconn.cursor()
				c.execute('''SELECT min(id), temp, humid, datetime FROM ENV WHERE sent=0''')
				db_res=c.fetchone()
				print("SQL Queried")
				if db_res[0] is not None:
					retstr=str(db_res[3])
					retstr+="t:"+str(db_res[1])
					retstr+="h:"+str(db_res[2])
					print("Data exists")
					retstr=[retstr, db_res[0]]
					return retstr
				else:
					print("up to date")
			except Exception as e:
				print(e)
			finally:
				dbconn.close()

		except:
			print("IO Error")
		#if error/nothing to send
		#time.sleep(5)

def updateDBRecord(id):
	try:
		dbconn=sqlite3.connect("envdata.db")
		c=dbconn.cursor()
		c.execute('UPDATE ENV SET sent=1 WHERE ID=?', [int(id)])
		dbconn.commit()
		dbconn.close()
		return True
	except:
		print("cant update record, retrying in 5 seconds")
		return False

def mainLoop():
	account=server.load_account(keypair.public_key)
	print("account fetched")
	fee=server.fetch_base_fee()
	#Run everything!
	while True:
		print("main loop")
		#Construct TXN
		data=getNextData()
		memo_to_write=str(data[0])

		txn=TransactionBuilder(
			source_account=account,
			network_passphrase=NET_PASS,
			base_fee=fee
			).add_text_memo(memo_to_write).append_payment_op(
				destination=keypair.public_key,
				asset_code="XLM",
				amount="0.00001").set_timeout(100000).build()

		#sign and submit
		txn.sign(keypair)
		while sendTXN(txn) is False:
			time.sleep(4)

		while updateDBRecord(data[1]) is False:
			time.sleep(5)
		print("txn sent, db updated")

getKeysSettings()

#wait until account exists and has sufficient starting balance
while accReady() is not True:
	time.sleep(20)

mainLoop()

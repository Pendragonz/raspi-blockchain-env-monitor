from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import Adafruit_DHT
import time
import sys
import getopt
from decimal import Decimal

import json
import pickle

#Define sensor type and GPIO pin
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=4

#Set up run conditions based on parameters TODO
INTERVAL=20
TEMP_ON=True
HUMID_ON=True


#Load keypair and settings from filesystem
f=open('keys.txt', 'r')
keyData=f.read()
f.close()

#Process data and set up global variables
listKeyData=[x.strip() for x in keyData.split(',')]

#CHANGE URL TO MAINNET URL!
if listKeyData[0] == "MAINNET":
	apiAddr="https://horizon.stellar.org/"
	server=Server(apiAddr)
	NET_PASS=Network.PUBLIC_NETWORK_PASSPHRASE
else:
	apiAddr="https://horizon-testnet.stellar.org/"
	server=Server(apiAddr)
	NET_PASS=Network.TESTNET_NETWORK_PASSPHRASE

keypair=Keypair.from_secret(listKeyData[2])

#check if accound exists and balance is >= 1.5 or loop until it is.
balance_valid=False
while balance_valid is not True:
	res=requests.get(apiAddr+"accounts/"+keypair.public_key)
	if res.status_code == 200:
		print("address valid")
		try:
			res_as_json=json.loads(res.text)
			bal=res_as_json["balances"][0]['balance']
			print("balance: " + bal)
		except:
			print("error fetching balance. balance likely 0. please send at least 1.5XLM")
			time.sleep(20)
		else:
			if float(bal) >= 1.5:
				#everything is perfect, break out of loop
				balance_valid=True
			else:
				print("balance not high enough")
				time.sleep(20)
	else:
		print("err fetching account. stat code: " + res.status_code + " account possibly not created")
		time.sleep(20)


#Run everything!
ON=True
running_total_temp=0
running_total_humid=0
num_readings=0
start=time.time()
end=start+INTERVAL
TOTAL_TXNS_CREATED=0


while ON:
	humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

	running_total_temp+=temperature
	running_total_humid+=humidity

	num_readings+=1

	if time.time() >= end:
		#Calculate averages
		avg_temp=running_total_temp/num_readings
		avg_humid=running_total_humid/num_readings

		#Limit avgs to  2dp
		avg_temp=Decimal(avg_temp)
		avg_temp=round(avg_temp,2)
		avg_humid=Decimal(avg_humid)
		avg_humid=round(avg_humid, 2)

		#Construct TXN
		t_hms=time.localtime()[3:6]
		memo_to_write="ti"+str(t_hms[0])+":"+str(t_hms[1])
		memo_to_write+=":"+str(t_hms[2])
		if TEMP_ON:
			memo_to_write+="te:"+str(avg_temp)
		if HUMID_ON:
			memo_to_write+="hu:"+str(avg_humid)

		account=server.load_account(keypair.public_key)

		txn=TransactionBuilder(
			source_account=account,
			network_passphrase=NET_PASS,
			base_fee=server.fetch_base_fee()
			).add_text_memo(memo_to_write).append_payment_op(
				destination=keypair.public_key,
				asset_code="XLM",
				amount="1").set_timeout(45).build()

		TOTAL_TXNS_CREATED=TOTAL_TXNS_CREATED+1
		#save unsigned txn to fs
		fname="txs/txn:"+str(TOTAL_TXNS_CREATED)+".dat"
		with open(fname, "wb") as f:
			pickle.dump(txn, f, 4)
		
		#sign and submit
		txn.sign(keypair)
		print("submitting tx " + TOTAL_TXNS_COMPLETED )
		response=server.submit_transaction(txn)

		#Reset Loop Variables TODO turn this into a function.
		running_total_temp=0
		running_total_humid=0
		num_readings=0
		end=time.time()+INTERVAL


from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import Adafruit_DHT
import time
import sys
import getopt
from decimal import Decimal

import pickle

#Define sensor type and GPIO pin
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=4

#Set up run conditions based on parameters TODO
INTERVAL=20
ID_NO="01"
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
	server=Server("https://horizon-testnet.stellar.org")
	NET_PASS=Network.TESTNET_NETWORK_PASSPHRASE
else:
	server=Server("https://horizon-testnet.stellar.org")
	NET_PASS=Network.TESTNET_NETWORK_PASSPHRASE

keypair=Keypair.from_secret(listKeyData[2])
account=server.load_account(keypair.public_key)


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
		memo_to_write=str(ID_NO)+"ti"+str(t_hms[0])+":"+str(t_hms[1])
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
		response=server.submit_transaction(txn)

		#Reset Loop Variables TODO turn this into a function.
		running_total_temp=0
		running_total_humid=0
		num_readings=0
		end=time.time()+INTERVAL


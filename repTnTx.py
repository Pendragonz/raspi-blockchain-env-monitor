from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests

import Adafruit_DHT
import time
import sys
import getopt
from decimal import Decimal

#Define Sensor Type and GPIO Pin
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=4

#Generate a random XLM private + public key
keypair = Keypair.random()
print("pub: " + keypair.public_key + " priv: " + keypair.secret)
f=open("pubkey.txt", "w")
f.write(keypair.public_key)
f.close()


#Request testnet XLM to use on stellar
url='https://friendbot.stellar.org'
response=requests.get(url, params={'addr':keypair.public_key})
print(response)


server=Server("https://horizon-testnet.stellar.org")
account=server.load_account(keypair.public_key)

txn = TransactionBuilder(
        source_account=account,
        network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
        base_fee=server.fetch_base_fee()
        ).add_text_memo("Hello World!").append_payment_op(
                destination=keypair.public_key,
                asset_code="XLM",
                amount="22").set_timeout(45).build()

txn.sign(keypair)
response=server.submit_transaction(txn)
print(response)

ON=True
INTERVAL=20

start=time.time()
end=start+INTERVAL
running_total_temp=0
running_total_humid=0
num_readings=0
while ON:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    running_total_temp=running_total_temp+temperature
    running_total_humid=running_total_humid+humidity

    num_readings=num_readings+1

    if time.time() >= end:
        #Calculate averages
        avg_temp=running_total_temp/num_readings
        avg_humid=running_total_humid/num_readings
        #Limit averages to 2dp
        avg_temp=Decimal(avg_temp)
        avg_humid=Decimal(avg_humid)
        avg_temp=round(avg_temp,2)
        avg_humid=round(avg_humid, 2)

        #Reset Loop Variables
        running_total_temp=0
        running_total_humid=0
        num_readings=0
        t=time.time()
        end=t+INTERVAL


        #Construct TXN
        t_hms=time.localtime()[3:6]
        memo_to_use="ti"+str(t_hms[0])+":"+str(t_hms[1])+":"+str(t_hms[2])+"te:" + str(avg_temp)+"hu:"+str(avg_humid)

        print(str(t_hms) + " averages taken")

        account=server.load_account(keypair.public_key)
        data_txn=TransactionBuilder(
            source_account=account,
            network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE,
            base_fee=server.fetch_base_fee()
            ).add_text_memo(memo_to_use).append_payment_op(
                destination=keypair.public_key,
                asset_code="XLM",
                amount="1").set_timeout(45).build()

        #Sign and submit
        data_txn.sign(keypair)
        response=server.submit_transaction(data_txn)
        print(response)

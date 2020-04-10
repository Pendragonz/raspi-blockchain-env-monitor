from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Account
import requests
import time
import sys
import getopt

#def mainloop
#def balance_check
#def gen_txn
#def send_txn




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
			if float(bal) >= 2.0:
				#everything is perfect, break out of loop
				balance_valid=True
			else:
				print("balance not high enough")
				time.sleep(20)
	else:
		print("err fetching account. stat code: " + res.status_code + " account possibly not created")
		time.sleep(20)

#Run everything!
while True:
	#Construct TXN
	t_=time.localtime()[1:6]

	memo_to_write
	memo_to_write

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

	#sign and submit
	txn.sign(keypair)
	while sendTXN(txn)=False:
		time.sleep(20)


def sendTXN():
	#code
	#response.code?
	response=server.submit_transaction(txn)
	if response != 200:
		return False
	return True

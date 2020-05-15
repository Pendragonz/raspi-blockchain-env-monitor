# raspi-blockchain-env-monitor

This repo is a compilation of the code written as part of my Individual Project for my final year at university.

Use this repo on your RaspberryPi alongside a DHT22 sensor attached to GPIO pin 4 in order to take readings and publish them to the Stellar blockchain.


## Prerequisites

### python3
### pip
### Adafruit_DHT
sudo pip install Adafruit_DHT
### stellar_sdk
pip install stellar_sdk==2.3.1
### Flask and Flask-HTTPAuth
pip install flask

pip install Flask-HTTPAuth
### SQLite3
sudo apt-get install sqlite3


## Running the monitoring service
To run the monitor, call:

python3 api.py

This will start the flask application on port 5000 on localhost. You can interact with it within your local network at 192.168.1.X:5000.
To find X, check your RaspberryPi's IP from within your router (192.168.1.1). To access it outside of your network, you'll need to setup port forwarding rules.

Keep in mind that the monitoring application api.py will carry on where it left off. If it was running on Stellar's mainnet it will resume once started. If it was running on Stellar's testnet it will do the same.
In order to stop the program properly use /refund.

### 192.168.1.X:5000/
This is the Flask app's homepage. It will display a link to the documentation here.

### 192.168.1.X:5000/register
This endpoint will display a form allowing you to register an account on the Pi. It will ask for a username and password. Don't lose these as there is no way to reset them without authorisation other than manually changing the code.
Additionally, note that only one user can be registered at a time.

### 192.168.1.X:5000/run
Providing the /run service hasn't already been activated, this endpoint will provide a form allowing you to start the monitor. Here you can choose the interval in which it will publish averaged readings. You can either run the monitor on Stellar's testnet or mainnet.

If you start it on the testnet, it will automatically request testnet funds in order to run, and begin monitoring.

If you choose to run the monitor on mainnet, it will create a local Stellar account and provide you with the Stellar address. The monitor will immediately begin taking temperature and humidity readings but will not publish these to Stellar before you add funds to the address.
You are required to send at least 1.1XLM in order for it to run. The amount you send should depend on the chosen publishing interval as well as usage duration expectation. More funds should be supplied before the monitor reaches a balance of 1.0XLM or it will cease to publish readings.

In order to aquire XLM, purchase some from a cryptocurrency exchange. Ensure you deposit your XLM from a personal wallet rather than an exchange wallet. The refund function only supports returning funds to the sender. Exchanges withdraw from different addresses from its deposit address, meaning your XLM will only be recoverable by contacting the exchange's support.

### 192.168.1.X:5000/get/pubkey
Returns NETWORK:PUBKEY

The network will either be MAINNET or TESTNET, and the PUBKEY will be the Stellar address the monitor is using.
To view the account, use an explorer like
https://stellar.expert/explorer/public - for mainnet
https://stellar.exoert/explorer/testnet - for testnet

### 192.168.1.X:5000/get/status
Returns any error messages the application outputs.

### 192.168.1.X:5000/reset
Stops any currently running services, deletes the registered user and backsup the local database and keyfile.

### 192.168.1.X:5000/refund
If the application is running on Stellar's mainnet, it will refund any unused XLM back to the sender.

It then performs the same tasks that /reset does and it then backs up the reading's database and Stellar wallet's keys to backups/ within the cloned directory.


## Running API.py on startup
In order to run the monitoring application on startup of your Pi use crontab.

Edit your crontab file:

sudo crontab -e

On the bottom line of the file, add the following:

@reboot cd /path/to/the/repo && python3 api.py &

## Visualising the readings from Stellar's blockchain

### Prerequisites
#### Python3
#### Plotly
pip install plotly
#### pandas
pip install pandas

### graph.py
Simply run graph.py and pass it your Stellar address (testnet not yet supported).

E.G:
  python graph.py GAZCFTIKK2MRFEF4APXO6OTQK4T5PIWQSHO3THENUIERHN7UB2XCOFA2
  python graph.py GDCCCKROG23MTXXDMMBZ7E2UIIGZJ3UYHU6CICWFPPJQ7CJ2NPO7XL4J


This will open up a chart in your default web browser. Two traces will be displayed, temperature and humidity.

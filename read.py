import Adafruit_DHT
import time
from decimal import Decimal
from os.path

import sqlite3

#Define sensor type and GPIO pin
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=4

#Set up run conditions based on parameters TODO
INTERVAL=20
#TOTAL_RECORDS=0

#setup DB.
path="envdata.db"
if !os.path.isFile(path):
	dbconn=sqlite3.connect(path)
	c = dbconn.cursor()
	c.execute('''CREATE TABLE ENV (temp FLOAT, humid FLOAT, datetime TEXT, sent BOOL)''')
	dbconn.commit()
	dbconn.close()

def foreverLoop():

	num_readings=0
	start=time.time()
	end=start+INTERVAL

	running_total_temp=0
	running_total_humid=0

	while True:
		humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
		running_total_temp+=temperature
		running_total_humid+=humidity

		num_readings+=1

		if time.time() >= end:
			#Calculate averages
			avg_temp=running_total_temp/num_readings
			avg_humid=running_total_humid/num_readings

			#Limit avgs to  2dp
			avg_temp=round(Decimal(avg_temp), 2)
			avg_humid=round(Decimal(avg_humid), 2)

			t_=time.localtime()[1:6]

			#Reset Loop Variables TODO turn this into a function.
			running_total_temp=0
			running_total_humid=0
			num_readings=0
			end=time.time()+INTERVAL

def writeToDB(temp, humid, datetime):
	vals=(temp, humid, datetime, FALSE)
	dbconn=sqlite3.connect(path)
	c=dbconn.cursor()
	c.execute('INSERT INTO ENV VALUES (?,?,?,?)', vals)
	dbconn.commit()
	dbconn.close()

#start subprocess send.py here
foreverLoop()

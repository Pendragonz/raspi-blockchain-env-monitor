
import Adafruit_DHT
import time
import datetime
from decimal import Decimal
import os.path
import subprocess
import sqlite3
import sys

#Define sensor type and GPIO pin
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=4

#Set up run conditions based on parameters
if len(sys.argv) > 1:
	INTERVAL=int(sys.argv[1])
	print("read.py interval set: " + str(INTERVAL))
else:
	INTERVAL=20

#setup DB.
path="envdata.db"
if os.path.isfile(path) is not True:
	dbconn=sqlite3.connect(path)
	c = dbconn.cursor()
	c.execute('''CREATE TABLE ENV (id INTEGER PRIMARY KEY, temp FLOAT, humid FLOAT, datetime TEXT, sent INTEGER)''')
	dbconn.commit()
	dbconn.close()
	print("table created")

def mainLoop():

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

			#Round avgs to  2dp
			avg_temp=round(Decimal(avg_temp), 2)
			avg_humid=round(Decimal(avg_humid), 2)

			#set avgs to dp
			avg_temp="%.2f"%float(avg_temp)
			avg_humid="%.2f"%float(avg_humid)

			#format date time to;  Month/Day;hour:minute:second e.g. 10/12;14:45:12
			#t_=time.localtime()[1:6]
			#dt=str(t_[1]) + "/"+ str(t_[0]) + ";" + str(t_[2])+":"+str(t_[3])+":"+str(t_[4])
			dt="{0:%d-%m;%H:%M:%S}".format(datetime.datetime.now())


			#Keep trying to add it to the db
			while writeToDB(avg_temp, avg_humid, dt) is not True:
				time.sleep(5)

			print('vals written to db' + " interval: " + str(INTERVAL))

			#Reset Loop Variables
			running_total_temp=0
			running_total_humid=0
			num_readings=0
			end=time.time()+INTERVAL

#need to add extra lines to check if data is actually being written.
def writeToDB(temp, humid, datetime):
	vals=[float(temp), float(humid), str(datetime), 0]
	print(vals)
	try:
		dbconn=sqlite3.connect(path)
		c=dbconn.cursor()
		c.execute('INSERT INTO ENV VALUES (NULL,?,?,?,?)', vals)
		dbconn.commit()
		dbconn.close()
		return True
	except:
		print("can't write to db")
		return False
#start subprocess send.py here
process=subprocess.Popen(["python3", "write.py"], shell=False)
mainLoop()

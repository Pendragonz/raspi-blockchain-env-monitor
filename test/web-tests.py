import requests
import unittest
import subprocess
import time
import os

import sqlite3

from shutil import copyfile, copytree

#api=None
#startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW




url="http://0.0.0.0:5050"

class TestHome(unittest.TestCase):
	api=None
	url=None
	HIDE=None

	def setUp(self):
		self.cleanTheSlate()
		self.url="http://0.0.0.0:5050"
		self.HIDE=open(os.devnull, "w")
		#self.api=subprocess.Popen(["flask", "run", "--host", "0.0.0.0", "--port", "5050", "--no-reload"]) #, stdout=self.HIDE#)
		self.api=subprocess.Popen(["python3", "api.py", "5050", "&"], shell=False, stdout=self.HIDE)
		#print("SUBPROCESS STARTED =====================")
		time.sleep(3)

	def tearDown(self):
		self.api.terminate()
		self.api.wait()
		time.sleep(1)
		#print("SUBPROCESS TERMINATED ===============")
		self.cleanTheSlate()
		self.HIDE.close()

	#deletes all api.py artifacts.
	def cleanTheSlate(self):
		try:
			os.remove("users.db")
		except OSError:
			pass

		try:
			os.remove("envdata.db")
		except OSError:
			pass

		try:
			os.remove("keys.txt")
		except OSError:
			pass

		try:
			os.remove("status.txt")
		except OSError:
			pass

		try:
			os.remove("mainrunning.txt")
		except OSError:
			pass

		try:
			os.remove("testnetrunning.txt")
		except OSError:
			pass


	def test_home(self):
		self.assertEqual(requests.get(url+"/").status_code, 200)

	def test_register(self):
		uname="daniel"
		pword="password"

		self.register(uname, pword)
		time.sleep(1)
		self.assertTrue(self.check_uname_in_db(uname))
	
	def register(self, uname, pword):
		data={'username': str(uname), 'password':str(pword)}
		reg_url=url+"/register_submit"
		requests.post(reg_url, data=data)
		

	def check_uname_in_db(self, username):
		userdb=sqlite3.connect("users.db")
		curs=userdb.cursor()
		curs.execute('SELECT * FROM users WHERE username=?', [username])
		res=curs.fetchone()
		userdb.close()
		return res
		


	def test_run_testnet(self):
		uname="daniel"
		pword="password"
		self.register(uname, pword)
		run_url=url+"/run_submit"
		data={'NETWORK': 'TESTNET', 'INTERVAL': '2'}
		res=requests.post(run_url, data=data, auth=(uname, pword))
		#print(res.text)
		self.assertEqual(res.status_code, 200)
		
		time.sleep(10)
		num_entries = self.get_num_env_entries()
		#print(str(num_entries))
		self.assertTrue(int(num_entries) > 3)
		requests.get(url+"/reset", auth=(uname,pword))


	def get_num_env_entries(self):
		envdata=sqlite3.connect('envdata.db')
		c=envdata.cursor()
		c.execute('SELECT Count(*) FROM ENV')
		res=c.fetchone()
		envdata.close()
		return res[0]


#	def test_run_mainnet(self):
#		pass

#	def test_reset(self):
#		pass

#	def test_refund(self):
#		pass

#	def test_get_pubkey(self):
#		pass

copyfile('../api.py', 'api.py')
copyfile('../read.py', 'read.py')
copyfile('../write.py','write.py')
try:
	copytree('../templates', 'templates')
except Exception as e:
	pass

unittest.main()

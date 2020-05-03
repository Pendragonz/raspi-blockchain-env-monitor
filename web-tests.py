import requests
import unittest
import subprocess
import time
import os

url="http://127.0.0.1:5000"

#res=requests.get(url)
#print(res.text)

api=None

#startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

class TestHome(unittest.TestCase):
	api=None

	def setUp(self):
		self.cleanTheSlate()
		self.url="http://0.0.0.0:5000"
		self.api=subprocess.Popen(["python3", "api.py", "2>/dev/null"], shell=False)
		print("SUBPROCESS STARTED =====================")
		time.sleep(1)

	def tearDown(self):
		self.api.terminate()
		self.api.wait()
		print("SUBPROCESS TERMINATED ===============")
		self.cleanTheSlate()

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
		print("TEST_HOME CALLED=====================")
		print("url: " + url)
		self.assertEqual(requests.get(url+"/").status_code, 200)

	def test_register(self):
		pass

	def test_run_testnet(self):
		pass

	def test_run_mainnet(self):
		pass

	def test_reset(self):
		pass

	def test_refund(self):
		pass

	def test_get_pubkey(self):
		pass


unittest.main()

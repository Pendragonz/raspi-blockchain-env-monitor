from stellar_sdk import Keypair


"""
script to generate a keypair.
currently exclusivley used by web-tests.py
"""

keypair = Keypair.random()
str="TESTINGKEY, " + keypair.public_key + ", " + keypair.secret

with open("testing_keys.txt", "w") as f:
	f.write(str)

print(keypair.public_key)

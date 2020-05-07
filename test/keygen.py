from stellar_sdk import Keypair


keypair = Keypair.random()


str="TESTINGKEY, " + keypair.public_key + ", " + keypair.secret


with open("testing_keys.txt", "w") as f:
	f.write(str)

print(keypair.public_key)

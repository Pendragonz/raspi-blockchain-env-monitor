from stellar_sdk import Keypair


keypair = Keypair.random()



with open("testing_keys.txt", "w") as f:
	f.write(keypair.secret)

print(keypair.public_key)

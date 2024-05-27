import hashlib
import time
import json

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)
        print(f"Block {new_block.index} added to blockchain.")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash() or current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def print_blockchain(self):
        for block in self.chain:
            print("-----------------------------------------------------------------")
            print("Block Index:", block.index)
            print("Transactions:", block.transactions)
            print("Timestamp:", block.timestamp)
            print("Previous Hash:", block.previous_hash)
            print("Hash:", block.hash)
            print("-----------------------------------------------------------------")

# Create a new blockchain
blockchain = Blockchain()

def user_interface():
    while True:
        print("\nBlockchain Operations:")
        print("1. Add a new block")
        print("2. View the blockchain")
        print("3. Check blockchain validity")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            index = len(blockchain.chain)
            sender = input("Enter sender address: ")
            receiver = input("Enter receiver address: ")
            amount = input("Enter transfer amount: ")
            transactions = {
                "sender": sender,
                "recipient": receiver,
                "amount": amount
            }
            new_block = Block(index, transactions, blockchain.get_latest_block().hash)
            blockchain.add_block(new_block)

        elif choice == '2':
            blockchain.print_blockchain()

        elif choice == '3':
            if blockchain.is_chain_valid():
                print("The blockchain is valid.")
            else:
                print("The blockchain is not valid.")

        elif choice == '4':
            print("Exiting the blockchain program.")
            break

        else:
            print("Invalid choice, please try again.")

# Run the user interface
user_interface()

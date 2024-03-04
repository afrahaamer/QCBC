import hashlib
import time
import json

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp if timestamp is not None else time.time()  # Use provided timestamp or generate a new one
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "timestamp": self.timestamp,  # Include the timestamp in the hash calculation
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
        new_block.hash = new_block.calculate_hash()  # Calculate hash before adding the block
        self.chain.append(new_block)
        print(f"Blockchain {new_block.index} added")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Recalculate the hash to verify block integrity, now including the timestamp in the hash calculation
            if current_block.hash != current_block.calculate_hash():
                print(f"Block {current_block.index} hash mismatch!")
                print(f"Calculated hash: {current_block.calculate_hash()}")
                print(f"Stored hash: {current_block.hash}")
                return False

            if current_block.previous_hash != previous_block.hash:
                print(f"Block {current_block.index} previous hash mismatch!")
                print(f"Expected previous hash: {previous_block.hash}")
                print(f"Actual previous hash: {current_block.previous_hash}")
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

# Example usage
blockchain = Blockchain()
block1 = Block(1, {"sender": "Alice", "recipient": "Bob", "amount": 1}, blockchain.get_latest_block().hash)
blockchain.add_block(block1)

block2 = Block(2, {"sender": "Bob", "recipient": "Charlie", "amount": 2}, blockchain.get_latest_block().hash)
blockchain.add_block(block2)

blockchain.print_blockchain()
print()
print("Blockchain is valid:", blockchain.is_chain_valid())
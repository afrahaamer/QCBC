import hashlib
import time
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit_ibm_provider import IBMProvider
import numpy as np


provider = IBMProvider(token='4b0e46761fd74107c80eb85690e56159d465d8bcdc1d30940b7ce64161f13517444ca7b6e5f1764716ad226a41af43a53a5b864c6d37593f09d59aba18896b47') #Please change the API token to your own token here before running
firstchoice = input("Simulator(1) or Real quantum machine(2): ")
if firstchoice == '2':
    backend = provider.get_backend('ibm_brisbane') #Change the server if needed
    print("Accessing real quantum machine")
elif firstchoice == '1':
    backend = backend = Aer.get_backend('qasm_simulator')
    print("Accessing simulator")

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
        self.mining_accuracy = None  # Initialize mining accuracy attribute

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
        shared_key, error_rate = bb84_simulated_key_gen(len(str(new_block.transactions)) * 8)
        encrypted_transactions = xor_encrypt_decrypt(json.dumps(new_block.transactions), shared_key)
        new_block.transactions = encrypted_transactions  # Store encrypted transactions in the block
        binary_index = format(new_block.index, '03b')  # Assuming a small index for demonstration
        mining_success = mine(binary_index)
        if mining_success < 70:  # Example threshold
            print("Mining failed, block not added.")
            return
        
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()  # Recalculate hash with nonce
        new_block.mining_accuracy = mining_success  # Store the mining success (accuracy) in the block
        self.chain.append(new_block)
        print(f"Block {new_block.index} added with accuracy: {mining_success}%")

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
            print("\n-----------------------------------------------------------------")
            print("Block Index:", block.index)
            if isinstance(block.transactions, dict):
                print("Sender:", block.transactions.get('sender'))
                print("Receiver:", block.transactions.get('recipient'))
                print("Amount:", block.transactions.get('amount'))
            else:
                print("Transactions:", block.transactions)
            print("Mining Accuracy:", getattr(block, 'mining_accuracy', 'N/A'))  # Show accuracy if available
            print("Timestamp:", block.timestamp)
            print("Previous Hash:", block.previous_hash)
            print("Hash:", block.hash)
        print("-----------------------------------------------------------------\n")

def apply_hadamard(qc, qubits):
    for q in qubits:
        qc.h(q)
    return qc

def create_phase_oracle(input):
    oracle_circuit = QuantumCircuit(3, name="phase oracle")
    for x in range(3):
        if input[x] == '0':
            oracle_circuit.x(x)
    oracle_circuit.ccz(0, 1, 2)
    for x in range(3):
        if input[x] == '0':
            oracle_circuit.x(x)
    return oracle_circuit.to_gate()

def amplification_gate():
    amp_gate = QuantumCircuit(3, name="amplification gate")
    for x in range(3):
        amp_gate.x(x)
    amp_gate.ccz(0, 1, 2)
    for x in range(3):
        amp_gate.x(x)
    for x in range(3):
        amp_gate.h(x)
    return amp_gate.to_gate()

def mine(input):
    grover_circuit = QuantumCircuit(4, 3)
    grover_circuit.initialize('0000', grover_circuit.qubits)
    grover_circuit = apply_hadamard(grover_circuit, [0, 1, 2, 3])
    grover_circuit.append(create_phase_oracle(input), [0, 1, 2])
    grover_circuit = apply_hadamard(grover_circuit, [0, 1, 2, 3])
    grover_circuit.append(amplification_gate(), [0, 1, 2])
    grover_circuit.measure([0, 1, 2], [0, 1, 2])

    # Transpile the circuit for the specified backend
    transpiled_circuit = transpile(grover_circuit, backend)

    # Execute the transpiled circuit
    job = backend.run(transpiled_circuit, shots=8192)
    result = job.result()
    counts = result.get_counts()

    # Assuming the 'input' is the binary representation of 'something' to be found
    accuracy = (counts.get(input[::-1], 0) / 8192) * 100
    return accuracy


def user_interface():
    blockchain = Blockchain()
    while True:
        print("\nBlockchain Operations:")
        print("1. Add a new block")
        print("2. View the blockchain")
        print("3. Check blockchain validity")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            sender = input("Enter sender address: ")
            receiver = input("Enter receiver address: ")
            amount = input("Enter transfer amount: ")
            transaction = {"sender": sender, "recipient": receiver, "amount": amount}
            new_block = Block(len(blockchain.chain), transaction, blockchain.get_latest_block().hash)
            blockchain.add_block(new_block)
        elif choice == '2':
            blockchain.print_blockchain()
        elif choice == '3':
            if blockchain.is_chain_valid():
                print("Blockchain is valid.")
            else:
                print("Blockchain is not valid!")
        elif choice == '4':
            break
        else:
            print("Invalid choice, please choose again.")

def bb84_simulated_key_gen(key_length=20):
    # Alice generates random bits and bases
    alice_bits = np.random.randint(2, size=key_length)
    alice_bases = np.random.randint(2, size=key_length)

    # Bob chooses random bases
    bob_bases = np.random.randint(2, size=key_length)
    
    # Bob's measurement in chosen bases
    bob_bits = [alice_bits[i] if alice_bases[i] == bob_bases[i] else np.random.randint(2) for i in range(key_length)]
    
    # Alice and Bob keep the bits with the same basis
    shared_key = [alice_bits[i] for i in range(key_length) if alice_bases[i] == bob_bases[i]]
    bob_shared_key = [bob_bits[i] for i in range(key_length) if alice_bases[i] == bob_bases[i]]

    # Compare Alice and Bob's shared keys to detect eavesdropping
    error_rate = sum(1 for i in range(len(shared_key)) if shared_key[i] != bob_shared_key[i]) / len(shared_key) if shared_key else 0

    return shared_key, error_rate

def xor_encrypt_decrypt(message, key):
    binary_message = ''.join(format(ord(x), 'b').zfill(8) for x in message)
    encrypted_binary = ''.join(str(int(binary_message[i]) ^ key[i % len(key)]) for i in range(len(binary_message)))
    
    # Convert encrypted binary back to string for simplicity
    encrypted_message = ''.join(chr(int(encrypted_binary[i:i+8], 2)) for i in range(0, len(encrypted_binary), 8))

    return encrypted_message

user_interface()
import hashlib
import time
import json
from qiskit import QuantumCircuit, Aer, execute
import numpy as np


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

    def calculate_hash_with_proof_of_work(self, difficulty):
        nonce = 0
        computed_hash = self.calculate_hash()
        while not computed_hash.startswith('0' * difficulty):
            nonce += 1
            self.timestamp = time.time()  # Update the timestamp for each attempt
            block_string = json.dumps({
                "index": self.index,
                "transactions": self.transactions,
                "timestamp": self.timestamp,
                "previous_hash": self.previous_hash,
                "nonce": nonce  # Include the nonce in the hash calculation
            }, sort_keys=True).encode()
            computed_hash = hashlib.sha256(block_string).hexdigest()
        return computed_hash, nonce

class Blockchain:
    def __init__(self):
        self.difficulty = 2   # Set the difficulty (number of leading zeros)
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash, nonce = new_block.calculate_hash_with_proof_of_work(self.difficulty)
        self.chain.append(new_block)
        print(f"Block {new_block.index} added to blockchain.")

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash() or current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def simulate_brute_force_attack(self, block_index):
        # This is a very simplified simulation where we just try to find a new hash for the altered transaction
        try:
            block = self.chain[block_index]
        except IndexError:
            print("Block not found.")
            return

        print(f"Simulating attack on Block {block_index}")
        original_transactions = block.transactions
        block.transactions = "Altered Transactions"  # Simulating an attack by altering transactions

        found = False
        attempts = 0
        while not found:
            attempts += 1
            block.timestamp += 1  # Altering the timestamp to simulate hash changes
            new_hash = block.calculate_hash()
            if new_hash.startswith("0000"):
                found = True

        print(f"Attack successful after {attempts} attempts. New Hash: {new_hash}")
        # Restore original transactions after simulation
        block.transactions = original_transactions
        block.hash = block.calculate_hash()

class QuantumBlockchain:
    def __init__(self, backend):
        self.chain = [self.create_genesis_block()]
        self.backend = backend

    def create_genesis_block(self):
        return Block(0, [], "0")

    def add_block(self, new_block):
        start_time = time.time()
        shared_key, error_rate = bb84_simulated_key_gen(len(str(new_block.transactions)) * 8)
        # Since shared_key is now correctly extracted, we can proceed.
        encrypted_transactions = xor_encrypt_decrypt(json.dumps(new_block.transactions), shared_key)
        new_block.transactions = encrypted_transactions  # Store encrypted transactions in the block
        # Simplified mining process: Use the block index as input for the mining function
        binary_index = format(new_block.index, '03b')  # Assuming a small index for demonstration
        mining_success = mine(binary_index, type_choice='1')
        if mining_success < 70:  # Example threshold
            print("Mining failed, block not added.")
            return
        
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()  # Recalculate hash with nonce
        new_block.mining_accuracy = mining_success  # Store the mining success (accuracy) in the block
        self.chain.append(new_block)
        print(f"Block {new_block.index} added with accuracy: {mining_success}%")
        end_time = time.time()
        print(f"Quantum Block {new_block.index} added in {end_time - start_time} seconds.")

    def get_latest_block(self):
        return self.chain[-1]
    def simulate_brute_force_attack(self, block_index):
        # This is a very simplified simulation where we just try to find a new hash for the altered transaction
        try:
            block = self.chain[block_index]
        except IndexError:
            print("Block not found.")
            return

        print(f"Simulating attack on Block {block_index}")
        original_transactions = block.transactions
        block.transactions = "Altered Transactions"  # Simulating an attack by altering transactions

        found = False
        attempts = 0
        while not found:
            attempts += 1
            block.timestamp += 1  # Altering the timestamp to simulate hash changes
            new_hash = block.calculate_hash()
            if new_hash.endswith("0000"):
                found = True


        print(f"Attack successful after {attempts} attempts. New Hash: {new_hash}")
        # Restore original transactions after simulation
        block.transactions = original_transactions
        block.hash = block.calculate_hash()



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

def mine(input, type_choice='1'):
    grover_circuit = QuantumCircuit(4, 3)
    grover_circuit.initialize('0000', grover_circuit.qubits)
    grover_circuit = apply_hadamard(grover_circuit, [0, 1, 2, 3])
    grover_circuit.append(create_phase_oracle(input), [0, 1, 2])
    grover_circuit = apply_hadamard(grover_circuit, [0, 1, 2, 3])
    grover_circuit.append(amplification_gate(), [0, 1, 2])
    grover_circuit.measure([0, 1, 2], [0, 1, 2])
    job = execute(grover_circuit, backend, shots=8192)
    result = job.result()
    counts = result.get_counts()
    # Assuming the 'input' is the binary representation of 'something' to be found
    accuracy = (counts.get(input[::-1], 0) / 8192) * 100
    return accuracy

def bb84_simulated_key_gen(key_length=20):
    # Step 1: Alice generates random bits and bases
    alice_bits = np.random.randint(2, size=key_length)
    alice_bases = np.random.randint(2, size=key_length)

    # Step 3: Bob chooses random bases
    bob_bases = np.random.randint(2, size=key_length)
    
    # Simulate Bob's measurement in chosen bases
    bob_bits = [alice_bits[i] if alice_bases[i] == bob_bases[i] else np.random.randint(2) for i in range(key_length)]
    
    # Step 4: Sifting - Alice and Bob only keep bits where they chose the same basis
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

# Example usage:
backend = Aer.get_backend('qasm_simulator')  # Default to simulator for quantum
quantum_blockchain = QuantumBlockchain(backend=backend)
traditional_blockchain = Blockchain()

def add_sample_blocks(blockchain, num_blocks=10):
    for i in range(1, num_blocks + 1):
        transactions = {
            "sender": f"sender_{i}",
            "recipient": f"recipient_{i}",
            "amount": i * 100  # Arbitrary amount
        }
        new_block = Block(index=i, transactions=transactions, previous_hash=blockchain.get_latest_block().hash)
        blockchain.add_block(new_block)

# Adding blocks to both blockchains
print("Adding blocks to the Quantum Blockchain")
add_sample_blocks(quantum_blockchain)
print("\nAdding blocks to the Traditional Blockchain")
add_sample_blocks(traditional_blockchain)

# Now simulate brute force attacks
print("\nSimulating Brute Force Attack on Quantum Blockchain's Block 2")
quantum_blockchain.simulate_brute_force_attack(2)

print("\nSimulating Brute Force Attack on Traditional Blockchain's Block 2")
traditional_blockchain.simulate_brute_force_attack(2)

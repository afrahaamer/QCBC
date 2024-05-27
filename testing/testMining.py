import hashlib
import time
import json
import numpy as np
from qiskit import QuantumCircuit, Aer, execute
import matplotlib.pyplot as plt
backend = backend = Aer.get_backend('qasm_simulator')

# Create a basic Block class that will be inherited by both implementations
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
    
# Define the classical Blockchain class
class ClassicalBlockchain:
    def __init__(self):
        self.difficulty = 3   # Set the difficulty (number of leading zeros)
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, [], "0")

    def add_block(self, new_block):
        start_time = time.time()
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash, nonce = new_block.calculate_hash_with_proof_of_work(self.difficulty)
        self.chain.append(new_block)
        end_time = time.time()
        print(f"Classical Block {new_block.index} added in {end_time - start_time} seconds.")

    def get_latest_block(self):
        return self.chain[-1]
    
# Define the quantum Blockchain class
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
        mining_success = mine(binary_index)
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
    job = execute(grover_circuit, backend, shots=8192)
    result = job.result()
    counts = result.get_counts()
    # Assuming the 'input' is the binary representation of 'something' to be found
    accuracy = (counts.get(input[::-1], 0) / 8192) * 100
    return accuracy

def bb84_simulated_key_gen(key_length=20):
    # Alice generates random bits and bases
    alice_bits = np.random.randint(2, size=key_length)
    alice_bases = np.random.randint(2, size=key_length)

    # Bob chooses random bases
    bob_bases = np.random.randint(2, size=key_length)
    
    # Simulate Bob's measurement in chosen bases
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
    
    encrypted_message = ''.join(chr(int(encrypted_binary[i:i+8], 2)) for i in range(0, len(encrypted_binary), 8))

    return encrypted_message

def test_block_mining(blockchain_type, backend=None):
    mining_times = []
    if blockchain_type == "classical":
        blockchain = ClassicalBlockchain()
    elif blockchain_type == "quantum":
        blockchain = QuantumBlockchain(backend)
    else:
        print("Invalid blockchain type")
        return mining_times

    for i in range(1, 6):  # Test with 5 blocks
        transactions = {"sender": "A", "recipient": "B", "amount": i * 10}
        new_block = Block(i, transactions, blockchain.get_latest_block().hash)
        mining_time = blockchain.add_block(new_block)
        if mining_time is not None:  # Make sure mining_time is not None
            mining_times.append(mining_time)
        else:
            mining_times.append(0)  # Append 0 or some default if mining failed
    return mining_times

def main():
    backend = Aer.get_backend('qasm_simulator')  # Default to simulator for quantum
    classical_times = test_block_mining("classical")
    quantum_times = test_block_mining("quantum", backend)

    # Plotting the comparison chart
    blocks = list(range(1, 6))
    plt.plot(blocks, classical_times, label='Classical Blockchain', marker='o')
    plt.plot(blocks, quantum_times, label='Quantum Blockchain', marker='s')
    plt.title('Block Mining Time Comparison')
    plt.xlabel('Block Number')
    plt.ylabel('Mining Time (seconds)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Call the main function
if __name__ == "__main__":
    main()

from qiskit import QuantumCircuit, Aer, execute
import numpy as np

# Parameters
n = 100  # Number of qubits / bits in the key
eavesdropping = True  # Set to False to simulate without eavesdropping

# Step 1: Key Generation by Alice
alice_bits = np.random.randint(2, size=n)
alice_bases = np.random.randint(2, size=n)  # 0 for Z basis, 1 for X basis

# Function to encode qubits based on Alice's bits and bases
def encode_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)
    if basis == 1:  # Prepare in X basis
        qc.h(0)
    if bit == 1:
        qc.x(0)
    if basis == 1:  # Back to Z basis if prepared in X
        qc.h(0)
    qc.measure(0, 0)
    return qc

# Bob's random choice of bases
bob_bases = np.random.randint(2, size=n)

# Simulate the transmission and measurement
backend = Aer.get_backend('qasm_simulator')
bob_results = []
for bit, alice_basis, bob_basis in zip(alice_bits, alice_bases, bob_bases):
    qc = encode_qubit(bit, alice_basis)
    if bob_basis == 1:  # Bob measures in X basis
        qc.h(0)
    result = execute(qc, backend, shots=1, memory=True).result()
    measured_bit = int(result.get_memory()[0])
    bob_results.append(measured_bit)

# Debugging: Print sample of bits and bases
print("Alice's bits (sample):", alice_bits[:10])
print("Alice's bases (sample):", alice_bases[:10])
print("Bob's bases (sample):", bob_bases[:10])
print("Bob's results (sample):", bob_results[:10])

# Step 4: Basis Reconciliation
matching_bases_indices = [i for i in range(n) if alice_bases[i] == bob_bases[i]]
print(f"Total matching bases: {len(matching_bases_indices)}")

# Error Checking to Detect Eavesdropping
# Use a larger sample size, e.g., 20% of the matching bits for a more stable error rate estimate
sample_size = int(len(matching_bases_indices) * 0.35)  # Adjusted from 0.1 to 0.2
sample_indices = np.random.choice(matching_bases_indices, sample_size, replace=False)

errors = sum(alice_bits[i] != bob_results[i] for i in sample_indices)
error_rate = errors / sample_size
print(f"Sampled bits for error checking: {sample_size}, Errors found: {errors}, Error rate: {error_rate}")

# Determine if eavesdropping is detected
threshold = 0.2  # Threshold for error rate
if error_rate > threshold:
    print("Eavesdropping detected! Abort key exchange.")
else:
    # Proceed with key generation from the remaining unmatched bits
    final_key_indices = [i for i in matching_bases_indices if i not in sample_indices]
    final_key = [bob_results[i] for i in final_key_indices]
    print("Final key generated successfully. Sample of the final key:", final_key[:20])

# Note: This simulation assumes ideal conditions and does not model actual quantum channel noise or imperfections.

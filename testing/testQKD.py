import time
import numpy as np
import matplotlib.pyplot as plt


# Function to test the key generation performance
def test_key_generation_performance(key_gen_func, iterations=100, key_length=20):
    total_time = 0
    for _ in range(iterations):
        start_time = time.time()
        key_gen_func(key_length)
        end_time = time.time()
        total_time += (end_time - start_time)
    average_time = total_time / iterations
    return average_time
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

def b92_simulated_key_gen(key_length=20, error_rate=0.1):
    # Initialize the key and test set
    shared_key = []
    test_set = []

    # Alice generates random bits and decides corresponding non-orthogonal states
    # 0 -> |0⟩, 1 -> |+⟩
    alice_bits = np.random.randint(2, size=key_length)

    # Bob measures in a random basis where 0 means measure in |+⟩, 1 means measure in |−⟩ basis
    bob_bases = np.random.randint(2, size=key_length)
    bob_results = []

    # Simulate the channel and potential eavesdropper introducing errors
    for i in range(key_length):
        if np.random.random() < error_rate:  # Introduce error with the given probability
            bob_measure = (alice_bits[i] + 1) % 2  # Flip the bit to simulate error
        else:
            bob_measure = alice_bits[i]  # When no error, Bob measures the same as Alice sent

        bob_results.append(bob_measure)

    # Bob only keeps the result if he measured the opposite of what Alice sent
    for i in range(key_length):
        if bob_bases[i] != alice_bits[i]:
            shared_key.append(bob_results[i])

    # Pick a subset of the bits to compare for errors
    num_test_bits = int(key_length * 0.1)
    test_indices = np.random.choice(range(len(shared_key)), size=num_test_bits, replace=False)
    test_set = [shared_key[i] for i in test_indices]

    # Ensure alice_test_set has corresponding elements by checking valid indices
    alice_test_set = [alice_bits[i] for i in test_indices if i < len(alice_bits) and bob_bases[i] != alice_bits[i]]

    # Calculate the error rate based on the test set
    if len(test_set) == len(alice_test_set) and len(test_set) > 0:  # Check for non-empty and equal-length sets
        error_count = sum(1 for i in range(len(test_set)) if test_set[i] != alice_test_set[i])
        measured_error_rate = error_count / len(test_set)
    else:
        measured_error_rate = 0  # Default to zero error rate if sets are unequal or empty

    # Remove test bits from the shared key
    shared_key = [bit for i, bit in enumerate(shared_key) if i not in test_indices]

    return shared_key, measured_error_rate

# Perform the tests
key_lengths = range(10, 101, 10)  # Test key lengths from 10 to 100
bb84_times = [test_key_generation_performance(bb84_simulated_key_gen, key_length=k) for k in key_lengths]
b92_times = [test_key_generation_performance(b92_simulated_key_gen, key_length=k) for k in key_lengths]

# Plotting the results
plt.figure(figsize=(10, 5))
plt.plot(key_lengths, bb84_times, marker='o', label='BB84')
plt.plot(key_lengths, b92_times, marker='s', label='B92')

# Adding the title and labels
plt.title('Key Generation Time Comparison')
plt.xlabel('Key Length')
plt.ylabel('Average Time (seconds)')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
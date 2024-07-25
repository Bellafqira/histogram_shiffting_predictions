import hashlib
import numpy as np


def sha256_to_binary_np_array(input_string):
    # Compute the SHA-256 hash
    sha256_hash = hashlib.sha256(input_string.encode()).digest()

    # Convert the hash to a binary representation (a sequence of bits)
    binary_representation = ''.join(format(byte, '08b') for byte in sha256_hash)

    # Convert the binary string to a list of integers (0 or 1)
    binary_list = [int(bit) for bit in binary_representation]

    # Convert the list to a NumPy array
    binary_np_array = np.array(binary_list, dtype=np.uint8)

    return binary_np_array


# # Example usage
# input_string = "Hello, World!"
# binary_np_array = sha256_to_binary_np_array(input_string)
# print(binary_np_array)


def generate_random_binary_array_from_string(seed_string, array_size):
    # Compute the SHA-256 hash of the seed string
    sha256_hash = hashlib.sha256(seed_string.encode()).digest()

    # Convert the hash to an integer seed
    seed = int.from_bytes(sha256_hash, 'big')

    # Initialize the NumPy random generator with the derived seed
    rng = np.random.default_rng(seed)

    # Generate a random binary array
    random_binary_array = rng.integers(0, 2, size=array_size, dtype=np.uint8)

    return random_binary_array


# # Example usage
# seed_string = "Hello, World!"
# array_size = (10,)  # Change this to the desired array size
# random_binary_array = generate_random_binary_array_from_string(seed_string, array_size)
# print(random_binary_array)

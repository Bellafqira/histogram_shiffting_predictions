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


def reshape_and_compute(binary_array):

    # Trim the array to a multiple of 256
    trimmed_length = (binary_array.size // 256) * 256
    trimmed_array = binary_array[:trimmed_length]

    # Reshape the array into rows of 256
    reshaped_array = trimmed_array.reshape(-1, 256)

    result_array = np.where(np.sum(reshaped_array, axis=0) > (reshaped_array.shape[0] / 2), 1, 0)

    return result_array

# # Example usage
# binary_array = np.random.randint(0, 2, size=(3123,), dtype=np.uint8)
#
# # Compute mean
# mean_result = reshape_and_compute(binary_array, method='mean')
# print(mean_result)
#
# # Compute majority vote
# majority_result = reshape_and_compute(binary_array, method='majority')
# print(majority_result)


def compute_ber(array1, array2):
    """
    Compute the Bit Error Rate (BER) between two binary NumPy arrays.

    Parameters:
    - array1: First binary NumPy array.
    - array2: Second binary NumPy array.

    Returns:
    - ber: Bit Error Rate (BER) between the two arrays.
    """
    if array1.shape != array2.shape:
        raise ValueError("Input arrays must have the same shape.")

    # Compute the number of bit errors
    bit_errors = np.sum(array1 != array2)

    # Compute the total number of bits
    total_bits = array1.size

    # Compute the BER
    ber = bit_errors / total_bits

    return ber

# # Example usage
# array1 = np.random.randint(0, 2, size=(3123,), dtype=np.uint8)
# array2 = np.random.randint(0, 2, size=(3123,), dtype=np.uint8)
#
# ber = compute_ber(array1, array2)
# print(f"Bit Error Rate (BER): {ber}")


def compute_psnr(original, compressed):
    """
    Compute the Peak Signal-to-Noise Ratio (PSNR) between two 2D NumPy arrays.

    Parameters:
    - original: First 2D NumPy array (original image).
    - compressed: Second 2D NumPy array (compressed image).

    Returns:
    - psnr: Peak Signal-to-Noise Ratio (PSNR) between the two arrays.
    """
    if original.shape != compressed.shape:
        raise ValueError("Input arrays must have the same shape.")

    mse = np.mean((original - compressed) ** 2)
    if mse == 0:
        return float('inf')

    max_pixel = 255.0  # Assuming the pixel values range from 0 to 255
    psnr = 20 * np.log10(max_pixel / np.sqrt(mse))

    return psnr
import hashlib
from copy import deepcopy

import numpy as np
from PIL import Image
from utils.utils import sha256_to_binary_np_array, generate_random_binary_array_from_string
import json
import os
from datetime import datetime

def embed_watermark(conf):
    original_image_path, message, watermarked_image_path, secret_key = (conf["original_image_path"], conf["message"],
                                                                        conf["watermarked_image_path"],
                                                                        conf["secret_key"])

    kernel, stride = conf["kernel"], conf["stride"]
    # Get the threshold
    t_hi = conf["T_hi"]

    watermark = sha256_to_binary_np_array(message + secret_key)

    image = Image.open(original_image_path).convert('L')
    image_np = np.array(image)

    original_image_copy = deepcopy(image_np)

    image_height, image_width = image_np.shape
    kernel_height, kernel_width = kernel.shape

    secret_key = generate_random_binary_array_from_string(secret_key, image_height * image_width)

    # Calculate the dimensions of the predictions image
    output_height = (image_height - kernel_height) // stride + 1
    output_width = (image_width - kernel_width) // stride + 1

    # idx of the watermark and the secret key
    idx_wat = 0
    idx_secret_key = 0

    # Overflow indices
    overflow_array = []

    # Perform the embedding with the convolution
    print("start ... 1. Perform the embedding ...")
    for y in range(0, output_height):
        for x in range(0, output_width):
            if secret_key[idx_secret_key] == 1:
                # Extract the current region of interest
                region = image_np[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                # Perform element-wise multiplication and sum the result
                neighbours = np.sum(region * kernel) // 1

                center = image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2]
                error = center - neighbours

                if error >= 0:
                    if center == 254:
                        image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] += 1
                        overflow_array.append(1)
                        idx_secret_key += 1
                        continue
                    elif center == 255:
                        overflow_array.append(0)
                        idx_secret_key += 1
                        continue

                    error_w, bit = embedding_value(error, t_hi, watermark[idx_wat % 256])
                    pix_wat = neighbours + error_w

                    image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat

                    if bit == 0 or bit == 1:
                        idx_wat += 1

                idx_secret_key += 1
            else:
                idx_secret_key += 1

    #  Perform the embedding starting by the last regions
    if len(overflow_array) != 0:
        idx_overflow = len(overflow_array)
        # Perform the embedding with the convolution
        print("start ... 2. Overflow management ...")
        for y in range(output_height-1, -1, -1):
            for x in range(output_width-1, -1, -1):
                if idx_overflow == -1:
                    break
                if secret_key[idx_secret_key-1] == 1:
                    # Extract the current region of interest
                    region = original_image_copy[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                    # Perform element-wise multiplication and sum the result
                    neighbours = np.sum(region * kernel)//1
                    center = original_image_copy[y * stride + kernel_height // 2, x * stride + kernel_width // 2]
                    error = center - neighbours

                    if error >= 0:
                        if center == 254 or center == 255:
                            idx_secret_key -= 1
                            continue
                        error_w, bit = embedding_value(error, t_hi, overflow_array[idx_overflow-1])
                        pix_wat = neighbours + error_w
                        image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat

                        if bit == 0 or bit == 1:
                            idx_overflow -= 1

                    idx_secret_key -= 1
                else:
                    idx_secret_key -= 1


    #  Compute the SHA-256 hash
    input_string = message + conf["secret_key"]
    watermark = hashlib.sha256(input_string.encode()).digest()
    # Convert the hash to a binary representation (a sequence of bits)
    watermark = ''.join(format(byte, '08b') for byte in watermark)

    # hash the watermarked image, and make its hash as an id in the configs file
    img_bytes = image_np.tobytes()
    sha256 = hashlib.sha256()
    sha256.update(img_bytes)
    id_watermarked_image = sha256.hexdigest()

    # Update the infos in the configs file
    update_watermarking_info(conf, watermark, id_watermarked_image)
    # save then the image
    watermarked_image = Image.fromarray(np.uint8(image_np))
    watermarked_image.save(watermarked_image_path)
    print("The watermark embedding successfully")


def embedding_value(error: int, thresh_hi: int, bit: int):

    if error > thresh_hi:
        error_w = error + abs(thresh_hi) + 1
        x = None
    elif 0 <= error <= thresh_hi:
        error_w = 2 * error + bit
        x = bit
    else:
        error_w = None
        x = None
        Exception("problem with the embedding function")
    return error_w, x


def update_watermarking_info(cf, watermark, id):
    # Create a new entry for the watermarking process
    new_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "secret_key": cf["secret_key"],
        "message": cf["message"],
        "watermark": watermark,
        "kernel": cf["kernel"].tolist(),
        "stride": 2,
        "T_hi": 0,
    }

    # Check if the file exists
    if os.path.exists(cf["configs_path"]):
        with open(cf["configs_path"], 'r') as file:
            data = json.load(file)
    else:
        data = {}

    if id not in data.keys():
        # Append the new entry to the existing data
        data[id] = new_entry

    # Save the updated data back to the JSON file
    with open(cf["configs_path"], 'w') as file:
        json.dump(data, file, indent=4)

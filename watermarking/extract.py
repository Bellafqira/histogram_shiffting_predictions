import hashlib
import json
import math
import os
from copy import deepcopy

import numpy as np
from PIL import Image

from utils.utils import generate_random_binary_array_from_string


def extract_watermark(conf):

    watermarked_image_path, recovered_image_path, extracted_watermark_path, = (
        conf["watermarked_image_path"], conf["recovered_image_path"], conf["extracted_watermark_path"])

    watermarked_image = Image.open(watermarked_image_path).convert('L')
    watermarked_image_np = np.array(watermarked_image)

    #  hash of the watermarked image

    img_bytes = watermarked_image_np.tobytes()
    sha256 = hashlib.sha256()
    sha256.update(img_bytes)
    id_watermarked_image = sha256.hexdigest()

    # Read the configs file
    # Check if the file exists
    if os.path.exists(conf["configs_path"]):
        with open(conf["configs_path"], 'r') as file:
            data = json.load(file)
    else:
            data = {}
            Exception("configs file does not exist")

    if id_watermarked_image in data.keys():
        configs = data[id_watermarked_image]
    else:
        configs = {}
        Exception("*****************No watermark match the one embedded in the watermarked "
                  "image*************************")


    secret_key = configs["secret_key"]
    kernel, stride = np.array(configs["kernel"]), configs["stride"]

    t_hi = configs["T_hi"]

    # Get the dimensions of the image and the kernel
    image_height, image_width = watermarked_image_np.shape
    kernel_height, kernel_width = kernel.shape

    secret_key = generate_random_binary_array_from_string(secret_key, image_height * image_width)

    # Calculate the dimensions of the prediction image
    output_height = (image_height - kernel_height) // stride + 1
    output_width = (image_width - kernel_width) // stride + 1

    recovered_image = deepcopy(watermarked_image_np)

    # extracted watermark
    ext_watermark = []

    # idx of the watermark and the secret key
    idx_secret_key = 0

    # Overflow indices
    overflow_array_positions = []

    # Perform the extraction with the convolution
    print("start ... Perform the extraction ...")
    for y in range(0, output_height):
        for x in range(0, output_width):
            if secret_key[idx_secret_key] == 1:
                # Extract the current region of interest
                region = recovered_image[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                # Perform element-wise multiplication and sum the result
                neighbours = np.sum(region * kernel) // 1
                center = recovered_image[y * stride + kernel_height // 2, x * stride + kernel_width // 2]

                error_w = center - neighbours
                if error_w >= 0:
                    if center == 255:
                        overflow_array_positions.append((y * stride + kernel_height // 2, x * stride + kernel_width // 2))
                        idx_secret_key += 1
                        continue

                    error, bit = extraction_value(error_w, t_hi)

                    if bit == 0 or bit == 1:
                        # print(bit)
                        ext_watermark.append(bit)

                    pix_wat = neighbours + error
                    recovered_image[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat
                idx_secret_key += 1
            else:
                idx_secret_key += 1

    # Restore the overflow regions
    if len(overflow_array_positions) != 0:
        overflow_wat = ext_watermark[-len(overflow_array_positions):]
        for idx, pos in enumerate(overflow_array_positions):
            recovered_image[pos] -= overflow_wat[idx]
        ext_watermark = ext_watermark[:-len(overflow_array_positions)-1]

    # Save to a binary watermark file
    np.save(extracted_watermark_path, np.array(ext_watermark))

    print("The watermark extracted successfully")
    recovered_image = Image.fromarray(np.uint8(recovered_image))
    recovered_image.save(recovered_image_path)


def extraction_value(error_w: int, thresh_hi: int):
    bit = None

    if error_w > (2*thresh_hi + 1):
        error = error_w - thresh_hi - 1
    else:
        bit = error_w % 2
        error = (error_w - bit) // 2

    return error, bit



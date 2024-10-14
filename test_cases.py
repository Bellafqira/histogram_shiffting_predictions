import hashlib
import json
import os
import unittest

import numpy as np
from PIL import Image

from utils.utils import sha256_to_binary_np_array, reshape_and_compute, compute_ber, compute_psnr
from watermarking.embed import embed_watermark
from configs import cf_embed, cf_extract
from watermarking.extract import extract_watermark

config_embed = cf_embed.cf_01
config_extract = cf_extract.cf_01

cf_test = config_embed | config_extract


class TestCases(unittest.TestCase):
    def tests(self):
        # Set the seed
        print("Test Embedding watermark")
        embed_watermark(config_embed)
        print("Test Extracting watermark")
        extract_watermark(config_extract)
        print("Test Comparing watermarks")
        compare_wat(cf_test)
        print("Test Computing PSNR")
        compare_psnr(cf_test)


if __name__ == '__main__':
    unittest.main()


def compare_wat(conf, jsonfile=None):

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
            Exception("config logs file does not exist")

    if id_watermarked_image in data.keys():
        configs = data[id_watermarked_image]
    else:
        configs = {}
        Exception("*****************No watermark match the one embedded in the watermarked "
                  "image*************************")

    # I need the size of the image
    original_image_path = conf["original_image_path"]
    original_image = Image.open(original_image_path).convert('L')
    original_image = np.array(original_image)
    image_height, image_width = original_image.shape

    # I need to read the extracted watermark and get the len of the watermak to know the capacity of the scheme
    watermark_path = conf["extracted_watermark_path"]
    watermark_extracted = np.load(watermark_path)

    print("The capacity of watermarking == ", len(watermark_extracted)/(image_height*image_width), "and the shape = ",
          len(watermark_extracted))

    # Generate the original watermark from the message and the secret key using SHA256
    message = conf["message"]
    secret_key = conf["secret_key"]
    timestamp = configs["timestamp"]

    watermark_original = sha256_to_binary_np_array(message + secret_key + timestamp)

    # watermark_original = sha256_to_binary_np_array(message + secret_key)
    # reshape the original watermark to the size of the extracted watermark
    watermark_original = np.tile(watermark_original, len(watermark_extracted)//len(watermark_original) + 1)

    if watermark_original.size > watermark_extracted.size:
        watermark_original = watermark_original[:watermark_extracted.size]

    # Comparison of the watermarks using the BER as a metric
    print("compute BER without the majority vote == ", compute_ber(watermark_original, watermark_extracted))

    # I do a majority vote to get a watermark of size 256. This could be interesting for a robust scheme
    watermark_extracted = reshape_and_compute(watermark_extracted)
    watermark_original = sha256_to_binary_np_array(message + secret_key + timestamp)

    # Comparison of the watermarks using the BER as a metric
    print("compute BER with the majority vote == ", compute_ber(watermark_original, watermark_extracted))


def compare_psnr(conf):
    # I need original image
    original_image_path, watermarked_image_path, recovered_image_path = (conf["original_image_path"],
                                                                         conf["watermarked_image_path"],
                                                                         conf["recovered_image_path"])

    # Load original Image
    original_image = Image.open(original_image_path).convert('L')
    original_image_np = np.array(original_image)
    #

    # Load watermarked Image
    watermarked_image = Image.open(watermarked_image_path).convert('L')
    watermarked_image_np = np.array(watermarked_image)

    # Load Recovered Image
    recovered_image = Image.open(recovered_image_path).convert('L')
    recovered_image_np = np.array(recovered_image)

    # Then compute psnr

    psnr = compute_psnr(original_image_np, watermarked_image_np)

    print("PSNR between watermarked and original== ", psnr)

    psnr = compute_psnr(original_image_np, recovered_image_np)

    print("PSNR between original and recovered==", psnr)



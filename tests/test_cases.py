import unittest

import numpy as np
from PIL import Image

from utils.utils import sha256_to_binary_np_array, reshape_and_compute, compute_ber, compute_psnr
from watermarking.embed import embed_watermark
from configs import conf_wat00
from watermarking.extract import extract_watermark


cf = conf_wat00.cf_01

class TestCases(unittest.TestCase):
    def test_embed(self):
        # Set the seed
        print("Test Embedding watermark")
        embed_watermark(cf)
        print("Test Extracting watermark")
        extract_watermark(cf)
        print("Test Comparing watermarks")
        compare_wat(cf)
        print("Test Computing PSNR")
        compare_psnr(cf)


if __name__ == '__main__':
    unittest.main()


def compare_wat(conf):

    # I need the size of the image
    original_image_path = conf["original_image_path"]
    original_image = Image.open(original_image_path).convert('L')
    original_image = np.array(original_image)
    image_height, image_width = original_image.shape

    # I need to read the extracted watermark and get the len of the watermak to know the capacity of the scheme
    watermark_path = conf["extracted_watermark_path"]
    watermark_extracted = np.load(watermark_path)

    print("The capacity of watermarking == ", len(watermark_extracted)/(image_height*image_width), "and the shape = ",
          watermark_extracted.shape)

    # watermark_extracted = reshape_and_compute(watermark_extracted)
    # print("watermark extracted after reshape", watermark_extracted[:100])
    # I do maybe a majority vote to get a watermark of size 256.
    message = conf["message"]
    watermark_original = sha256_to_binary_np_array(message)

    watermark_original = np.tile(watermark_original, len(watermark_extracted)//len(watermark_original) + 1)

    if watermark_original.size > watermark_extracted.size:
        watermark_original = watermark_original[:watermark_extracted.size]

    # Comparison of the watermarks using the BER as a metric
    print("compute BER == ", compute_ber(watermark_original, watermark_extracted))
    # sss
    print("positions == ", np.where(watermark_original != watermark_extracted)[0])


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



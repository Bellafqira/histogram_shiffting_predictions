import unittest

import numpy as np
from PIL import Image

from utils.utils import sha256_to_binary_np_array, reshape_and_compute, compute_ber, compute_psnr
from watermarking.embed import embed_watermark
from configs import conf_wat00
from watermarking.extract import extract_watermark


class TestCases(unittest.TestCase):
    def test_embed(self):
        print("Test Embedding watermark")
        embed_watermark(conf_wat00.cf_00)
        print("Test Extracting watermark")
        extract_watermark(conf_wat00.cf_00)
        print("Test Comparing watermarks")
        compare_wat(conf_wat00.cf_00)
        print("Test Computing PSNR")
        compare_psnr(conf_wat00.cf_00)


if __name__ == '__main__':
    unittest.main()


def compare_wat(conf):
    # I need to read the extracted watermark and get the len of the watermak to know the capacity of the scheme

    watermark_path = conf["extracted_watermark_path"]
    watermark_extracted = np.load(watermark_path)

    print("The capacity of watermarking == ", len(watermark_extracted)/(512*512), "and the shape = ", watermark_extracted.shape)
    watermark_extracted = reshape_and_compute(watermark_extracted)

    # I do maybe a majority vote to get a watermak of size 256.
    message = conf["message"]
    watermark_original = sha256_to_binary_np_array(message)
    # Comparison of the watermarks using the BER as a metric
    print("compute BER == ", compute_ber(watermark_original, watermark_extracted))


def compare_psnr(conf):

    # I need original image
    original_image_path, watermarked_image_path, recovered_image_path = (conf["original_image_path"],
                                                                         conf["watermarked_image_path"],
                                                                         conf["recovered_image_path"])

    # Load original Image
    original_image = Image.open(original_image_path).convert('L')
    original_image_np = np.array(original_image)

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



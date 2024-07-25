import numpy as np
from PIL import Image

from utils.utils import generate_random_binary_array_from_string


def extract_watermark(conf):

    watermarked_image_path, recovered_image_path, watermark_path  = conf["watermarked_image_path"], conf["recovered_image_path"], conf["extracted_watermark_path"]

    secret_key = conf["secret_key"]


    kernel, stride = conf["kernel"], conf["stride"]

    t_low, t_hi = conf["T_low"], conf["T_hi"]

    watermarked_image = Image.open(watermarked_image_path).convert('L')
    watermarked_image_np = np.array(watermarked_image)

    # Get the dimensions of the image and the kernel
    image_height, image_width = watermarked_image_np.shape
    kernel_height, kernel_width = kernel.shape

    secret_key = generate_random_binary_array_from_string(secret_key, image_height * image_width)

    # Calculate the dimensions of the output image
    output_height = (image_height - kernel_height) // stride + 1
    output_width = (image_width - kernel_width) // stride + 1

    # number of element selected by the kernel
    nonzero_kernel = np.count_nonzero(kernel)

    # extracted watermark
    ext_watermark = []

    # idx of the watermark and the secret key
    idx_secret_key = 0

    # Perform the extraction with the convolution
    print("Perform the extraction with the convolution")
    for y in range(0, output_height):
        for x in range(0, output_width):
            if secret_key[idx_secret_key] == 1:
                # Extract the current region of interest
                region = watermarked_image_np[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                # Perform element-wise multiplication and sum the result
                neighbours = np.sum(region * kernel) / nonzero_kernel
                center = watermarked_image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2]
                error_w = center - neighbours
                error, bit = extraction_value(error_w, t_low, t_hi)
                if bit == 0 or bit == 1 :
                    ext_watermark.append(bit)

                pix_wat = neighbours + error
                watermarked_image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat
                idx_secret_key += 1
            else:
                idx_secret_key += 1

    # Save to a binary file
    np.save(watermark_path, np.array(ext_watermark))

    recovered_image = Image.fromarray(np.uint8(watermarked_image_np))
    recovered_image.save(recovered_image_path)


def extraction_value(error_w:int, thresh_low:int, thresh_hi:int):
    bit = 5
    if error_w < (2*thresh_low - 1):
        error = error_w + abs(thresh_low) + 1
    elif error_w > (2*thresh_hi + 1):
        error = error_w - abs(thresh_hi) - 1
    else :
        bit = error_w % 2
        error = (error_w - bit)/2
    return error, bit
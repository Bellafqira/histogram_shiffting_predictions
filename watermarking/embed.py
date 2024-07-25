import numpy as np
from PIL import Image
from utils.utils import sha256_to_binary_np_array, generate_random_binary_array_from_string


def embed_watermark(conf):

    image_path, message, output_path, secret_key = conf["original_image_path"], conf["message"], conf["watermarked_image_path"], conf["secret_key"]

    kernel, stride = conf["kernel"], conf["stride"]

    t_low, t_hi = conf["T_low"], conf["T_hi"]

    watermark = sha256_to_binary_np_array(message)
    image = Image.open(image_path).convert('L')

    image_np = np.array(image)

    image_height, image_width = image_np.shape
    kernel_height, kernel_width = kernel.shape

    secret_key = generate_random_binary_array_from_string(secret_key, image_height*image_width)

    # Calculate the dimensions of the output image
    output_height = (image_height - kernel_height) // stride + 1
    output_width = (image_width - kernel_width) // stride + 1

    # number of element selected by the kernel
    nonzero_kernel = np.count_nonzero(kernel)

    # idx of the watermark and the secret key
    idx_wat = 0
    idx_secret_key = 0

    # Perform the embedding with the convolution
    print("Perform the embedding with the convolution")
    for y in range(0, output_height):
        for x in range(0, output_width):
            if secret_key[idx_secret_key] == 1:
                # Extract the current region of interest
                region = image_np[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                # Perform element-wise multiplication and sum the result
                neighbours = np.sum(region * kernel) / nonzero_kernel
                center = image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2]
                error = center - neighbours
                # print("error",  error, "center", center, "output[y, x]", output[y, x])
                pix_wat = neighbours + embedding_value(error, t_low, t_hi, watermark[idx_wat % 256 ])
                image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat
                idx_wat += 1
                idx_secret_key += 1
            else:
                idx_secret_key += 1

    watermarked_image_np = image_np
    watermarked_image = Image.fromarray(np.uint8(watermarked_image_np))
    watermarked_image.save(output_path)

def embedding_value(error:int, thresh_low:int, thresh_hi:int, bit:int):
    if error < thresh_low:
        error_w = error - abs(thresh_low) - 1
    elif error > thresh_hi:
        error_w = error + abs(thresh_hi) + 1
    elif thresh_low <= error < 0:
        error_w = 2*error - bit
    elif 0 <= error <= thresh_hi:
        error_w = 2 * error + bit
    else:
        error_w = None
        Exception("problem with the embedding function")
    return error_w

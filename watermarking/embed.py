import numpy as np
from PIL import Image
from utils.utils import sha256_to_binary_np_array, generate_random_binary_array_from_string


def embed_watermark(conf):
    original_image_path, message, watermarked_image_path, secret_key = (conf["original_image_path"], conf["message"],
                                                                        conf["watermarked_image_path"],
                                                                        conf["secret_key"])

    kernel, stride = conf["kernel"], conf["stride"]

    t_low, t_hi = conf["T_low"], conf["T_hi"]

    watermark = sha256_to_binary_np_array(message)

    image = Image.open(original_image_path).convert('L')
    image_np = np.array(image)

    image_height, image_width = image_np.shape
    kernel_height, kernel_width = kernel.shape

    secret_key = generate_random_binary_array_from_string(secret_key, image_height * image_width)

    # Calculate the dimensions of the predictions image
    output_height = (image_height - kernel_height) // stride + 1
    output_width = (image_width - kernel_width) // stride + 1

    # number of element selected by the kernel
    nonzero_kernel = np.count_nonzero(kernel)

    # idx of the watermark and the secret key
    idx_wat = 0
    idx_secret_key = 0

    # Perform the embedding with the convolution
    print("start ... Perform the embedding ...")
    for y in range(0, output_height):
        for x in range(0, output_width):
            if secret_key[idx_secret_key] == 1:
                # Extract the current region of interest
                region = image_np[y * stride:y * stride + kernel_height, x * stride:x * stride + kernel_width]
                # Perform element-wise multiplication and sum the result
                neighbours = np.sum(region * kernel) // nonzero_kernel
                center = image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2]
                error = center - neighbours

                error_w, bit = embedding_value(error, t_low, t_hi, watermark[idx_wat % 256])

                pix_wat = neighbours + error_w
                if pix_wat > 255:
                    print("overflow here .....................................")
                image_np[y * stride + kernel_height // 2, x * stride + kernel_width // 2] = pix_wat

                if bit == 0 or bit == 1:
                    idx_wat += 1
                idx_secret_key += 1
            else:
                idx_secret_key += 1

    watermarked_image_np = image_np
    watermarked_image = Image.fromarray(np.uint8(watermarked_image_np))
    watermarked_image.save(watermarked_image_path)
    print("The watermark embedding successfully")


def embedding_value(error: int, thresh_low: int, thresh_hi: int, bit: int):
    if error < thresh_low:
        error_w = error - abs(thresh_low) - 1
        x = 5
    elif error > thresh_hi:
        error_w = error + abs(thresh_hi) + 1
        x = 5
    elif thresh_low <= error < 0:
        error_w = 2 * error - bit
        x = bit
    elif 0 <= error <= thresh_hi:
        error_w = 2 * error + bit
        x = bit
    else:
        error_w = None
        x = None
        Exception("problem with the embedding function")
    return error_w, x

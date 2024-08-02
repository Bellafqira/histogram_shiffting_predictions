# Watermarking Project

This project presents a reversible watermarking scheme based on histogram shifting [1] on prediction errors [2] and an overflow management procedure. It supports only 2D images (e.g., grayscale Lena image).

[1] Sun, Y., Yuan, X., Liu, T., Huang, G., Lin, Z., & Li, J. (2023). FRRW: A feature extraction-based robust and reversible watermarking scheme utilizing zernike moments and histogram shifting. Journal of King Saud University-Computer and Information Sciences, 35(8), 101698.
[2] Naskar, R., & Subhra Chakraborty, R. (2013). Histogram‐bin‐shifting‐based reversible watermarking for colour images. IET Image Processing, 7(2), 99-110.

## Overview of the Proposed Watermarking Modulation

The proposed algorithm is composed of four steps:

### 1. Watermark Generation

We assume we have a message of type string that will be converted to a watermark coded into 256 bits using SHA256 and a secret key. We then generate a random sequence based on the secret key, which helps decide if a region of the image will be watermarked or not.

    watermark = SHA256(message || secret_key)
    random_sequence = PRNG(secret_key)

where || is the concatenation operator, and PRNG is a pseudo-random number generator.

### 2. Watermark Embedding

#### 2.1 Embedding Process

The inputs to the algorithm are: original image, watermark, kernel, stride, and threshold_high.

First, we check if the bit corresponding to the considered region of the random sequence generated above (`random_sequence`) is equal to 1. If it is not, we move to the next region. Otherwise, we apply the kernel to each region of the image to compute a prediction by region:

    prediction = region * kernel

where "*" is the convolution operator. Then we compute the error of the prediction between the center of the region and the prediction as follows:

    error = region_center - int(prediction)

In this work, we embed the watermark only in the regions/blocks where the corresponding `error` is greater than or equal to 0. Otherwise, we move to the next region.

#### 2.2 Watermarked Error Computation

Once the error is computed, the watermarked error (`error_w`) is computed as follows:

```python
# In this work, threshold_high is set to 0
# Initiate an empty list that will take the value 0 if the region center equals 255 and 1 if it equals 254. This procedure will resolve the overflowing problem in the histogram shifting scheme.

overflow_array = []
if error >= 0:
    if region_center == 254:
        overflow_array.append(1)
        pix_wat = 255
    elif region_center == 255:
        overflow_array.append(0)
        pix_wat = 255
    elif error > threshold_high:
        error_w = error + threshold_high + 1
        pix_wat = int(prediction) + error_w
    else:
        error_w = 2 * error + bit
        pix_wat = int(prediction) + error_w
else:
    continue
```

where "`bit0`" is a binary value from the watermark, and `pix_wat` is the watermarked value of the region center:

We then move by stride to the next region.

### 3. Watermark Extraction

The extraction process is described as follows:

#### 3.1 Inputs
- Watermarked image
- Secret key
- threshold_high

#### 3.2 Process
We start by generating the random sequence parameterized by the secret key, which helps identify if a region is watermarked or not. We apply the kernel to each region of the watermarked image to compute a prediction by region:

    prediction = region * kernel

where "*" is the convolution operator. We then compute the error of the prediction between the center of the watermarked region and the prediction:

    error_w = region_center - int(prediction)

#### 3.3 Watermarked Error Computation
The watermarked error is computed as follows:

```python
extracted_watermark = []
overflow_positions = []
if error_w >= 0:
    if region_center == 255:
        overflow_positions.append(region_center.position)
        # We keep in memory the positions of the overflow values to recover the original image quickly
    elif error_w > 2 * threshold_high + 1:
        error = error_w - threshold_high - 1
        pix_rec = int(prediction) + error
    else:
        bit = error_w % 2
        error = (error_w - bit) / 2
        pix_rec = int(prediction) + error
        extracted_watermark.append(bit)
```

where `bit` is the extracted bit, `extracted_watermark` is the extracted watermark, and `pix_rec` is the restored value of the region center.

We then move by stride to the next region to extract the watermark bits and restore the region center if it was modified.

If there was overflow in the extraction process, which means:

```python
len(overflow_positions) != 0
```
we first get the last `len(overflow_positions)` binary values from the watermark as:

```python
    last_bits = watermark[-len(overflow_positions):]
```
and we restore the overflow centers as follows:
```python
for idx, pos in enumerate(overflow_positions):
    recovered_image[pos] -= last_bits[idx]
```
The final extracted watermark will be:
```python
extracted_watermark = extracted_watermark[:-len(overflow_positions)-1]
```

### 4. Evaluation
#### 4.1 Watermark Comparison
We evaluate our scheme by comparing the original watermark with the extracted watermark using the Bit Error Rate (BER) as a metric. A post-process is applied to the extracted watermark using a majority vote for each 256-bit chunk. We then compare the extracted watermark with the original.

#### 4.2 Image Quality
We also evaluate the difference between the original and the watermarked image using the Peak Signal-to-Noise Ratio (PSNR).

## Requirements

To set up the project environment, you'll need:

- numpy~=1.23.5
- pillow~=10.4.0

## Setup

1. Clone the repository.
2. Navigate to the project directory.
3. Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```
5. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```




## Configuration File

This project includes several configuration files that allow you to customize various aspects of the watermarking process, such as the watermark, the secret key, and other parameters for embedding and extraction.

### Configuration Files

#### Embedding Configuration (`cf_embed.py`)
This file contains the configuration for the embedding step. Below is an example configuration:

```python
cf_00 = {
    "kernel": np.array([[0, 1 / 4, 0],
                        [1 / 4, 0, 1 / 4],
                        [0, 1 / 4, 0]]),  # Kernel to compute the prediction error
    "stride": 3,  # The size of the step to move the kernel. This should be greater than half the number of kernel rows + 1
    "T_hi": 0,  # Parameter of the histogram shifting

    "secret_key": "imt_atlantique",  # Secret key used to generate a random sequence that determines if a block will be watermarked or not

    "message": "SessionID_UserID_SenderID_ReceiverID_TimeStamp_DataID",
    # Seed to generate the watermark; the size of the watermark depends on the capacity in the image

    "original_image_path": "images/Lena.tiff",  # Path of the image to watermark

    "watermarked_image_path": "results/Lena_watermarked.tiff",  # Path to save the watermarked image

    "configs_path": "configs/config_logs.json"  # Path to save the watermarking parameters
}
```

#### Embedding Operation Log (`config_logs.json`)

This JSON file logs the parameters of each image watermarking operation. Each embedding operation is saved using the hash of the watermarked image as an identifier. This ensures image integrity, as one can hash the received watermarked image and verify if the hash exists in the config logs file. Below is an example entry in the config_logs.json file:

```python
  {
    "9d722523283dadba84bd9cbf7c1ec66ce280d08215801c906354b5bc2dd7849e": {
        "timestamp": "2024-08-01T16:27:30.576479Z",
        "secret_key": "imt_atlantique",
        "message": "a seed",
        "watermark": "0011111001000001010000100011001000010110111100111110101111111011001100010011100110001010011101100000011011000110110001111110110100011111000110100110110101010100100101101100011010101011001010000000001000000000111111101100000000101000110100111000110100101100",
        "kernel": [
            [0.0, 0.25, 0.0],
            [0.25, 0.0, 0.25],
            [0.0, 0.25, 0.0]
        ],
        "stride": 2,
        "T_hi": 0
    }
}

```
#### Extraction Configuration ([cf_extract.py]())

This file contains the configuration for extracting the watermark and restoring the original image from the watermarked image. Below is an example configuration:

```python
   cf_00 = {
         "watermarked_image_path": "results/Lena_watermarked.tiff",

         "recovered_image_path": "results/Lena_recovered.tiff",

         "extracted_watermark_path": "results/watermark_extracted.npy",

         "configs_path": "configs/config_logs.json"

         }
```

These configuration files provide a flexible way to manage and customize the watermarking process, ensuring that each step is properly documented and reproducible

## The following tests are provided:
    
```python
    
# Set the seed
print("Test Embedding watermark")
embed_watermark(config_embed)
print("Test Extracting watermark")
extract_watermark(config_extract)
print("Test Comparing watermarks")
compare_wat(cf_test)
print("Test Computing PSNR")
compare_psnr(cf_test)
   ```


## Running Tests

Run the following command to execute tests:

```bash
    python -m unittest tests.test_cases
```


## Contributing
Contributions are welcome. Please submit a pull request with your changes. If you have any questions, please contact reda.bellafqira@imt-atlantique.fr

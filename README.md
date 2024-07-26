# Watermarking Project

# Watermarking Project
This project presents a watermarking scheme inspired by Naskar and Subhra Chakraborty (2013) [1]. The scheme uses histogram shifting on the prediction errors and is reversible. It supports only 2D images (e.g., grayscale Lena image).

[1] Naskar, R., & Subhra Chakraborty, R. (2013). Histogram‐bin‐shifting‐based reversible watermarking for colour images. IET Image Processing, 7(2), 99-110.

## Overview of the Proposed Watermarking Modulation

The proposed algorithm is composed of four steps:

### 1. Watermark Generation

We assume we have a message of type string that will be converted to a watermark coded into 256 bits using SHA256. We then generate a random sequence based on the secret key, which helps decide if a region of the image will be watermarked or not.

### 2. Watermark Embedding

#### 2.1 Embedding Process

The inputs to the algorithm are: original image, watermark, kernel, stride, threshold_low, and threshold_high.

First, we check if the bit corresponding to the considered region of the random sequence generated above is equal to 1. If it is not, we move to the next region. Otherwise, we apply the kernel to each region of the image to compute a prediction by region:

\[ \text{prediction} = \text{region} \ast \text{kernel} \]

where \(\ast\) is the convolution operator. Then we compute the error of the prediction between the center of the region and the prediction as follows:

\[ \text{error} = \text{region\_center} - \text{int(prediction)} \]

#### 2.2 Watermarked Error Computation

Once the error is computed, the watermarked error is computed as follows:

```python
if error < threshold_low:
    error_w = error - abs(threshold_low) - 1
elif error > threshold_high:
    error_w = error + abs(threshold_high) + 1
elif threshold_low <= error < 0:
    error_w = 2 * error - bit
elif 0 <= error <= threshold_high:
    error_w = 2 * error + bit
return error_w
```

where "bit" is a binary value from the watermark. The watermarked value of the region center is then given as: 


    pix_wat = prediction + error

We then move by stride to the next region.

### 3. Watermark Extraction

The extraction process is described as follows:

#### 3.1 Inputs
- Watermarked image
- Secret key
- threshold_low
- threshold_high

#### 3.2 Process
We start by generating the random sequence parameterized by the secret key, which helps identify if a region is watermarked or not. We apply the kernel to each region of the watermarked image to compute a prediction by region:

    prediction = region ∗ kernel

where ∗ is the convolution operator. We then compute the error of the prediction between the center of the watermarked region and the prediction:

    error_w = region_center − int(prediction)

#### 3.3 Watermarked Error Computation
The watermarked error is computed as follows:

```python
if error_w < (2 * threshold_low - 1):
    error = error_w + abs(threshold_low) + 1
elif error_w > (2 * threshold_high + 1):
    error = error_w - abs(threshold_high) - 1
else:
    bit = error_w % 2
    if error_w < 0:
        error = (error_w + bit) / 2
    else:
        error = (error_w - bit) / 2
```


where "bit" is the extracted bit. The restored value of the region center is then given as:

    pix_wat = prediction + error

We then move by stride to the next region to extract the watermark bit and restore the region center if it was modified.

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

This project includes a configuration file that allows you to customize various aspects of the watermarking process, such as the watermark, the secret key, etc. (for embedding and extraction).

- `cf_wat00.py`: This file contains an example configuration to watermark the Lena image:

    ```python
    import numpy as np

    cf_00 = {
        "kernel": np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]),  # Kernel to compute the prediction error
        "stride": 2,  # The size of the step to move the kernel. This should be greater than half the number of kernel rows + 1
        
        "T_low": -1,  # Parameter of the histogram shifting (see [1] for more details)
        "T_hi": 1,  # Parameter of the histogram shifting (see [1] for more details)

        "secret_key": "imt_atlantique",  # Secret key used to generate a random sequence that determines if a block will be watermarked or not
        "message": "a seed",  # Seed to generate the watermark; the size of the watermark depends on the capacity in the image

        "original_image_path": "images/Lena.tiff",  # Path of the image to watermark

        "watermarked_image_path": "results/Lena_watermarked.tiff",  # Path to save the watermarked image

        "recovered_image_path": "results/Lena_recovered.tiff",  # Path to save the recovered image

        "extracted_watermark_path": "results/watermark_extracted.npy"  # Path to save the extracted watermark
    }
    ```

## Running Tests

Run the following command to execute tests:

   ```bash
    python -m unittest tests.test_cases
```
## The following tests are provided:
    
```python
    print("Test Embedding watermark")
    embed_watermark(conf_wat00.cf_00)
    print("Test Extracting watermark")
    extract_watermark(conf_wat00.cf_00)
    print("Test Comparing watermarks")
    compare_wat(conf_wat00.cf_00)
    print("Test Computing PSNR")
    compare_psnr(conf_wat00.cf_00)
   ```

## Contributing
Contributions are welcome. Please submit a pull request with your changes. If you have any questions, please contact reda.bellafqira@imt-atlantique.fr

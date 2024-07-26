# Watermarking Project

This project presents a watermarking scheme inspired by [1]. This scheme consists of histogram shifting on the prediction errors. It supports only 2D images (e.g., grayscale Lena image).

[1] Naskar, R., & Subhra Chakraborty, R. (2013). Histogram‐bin‐shifting‐based reversible watermarking for colour images. IET Image Processing, 7(2), 99-110.

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

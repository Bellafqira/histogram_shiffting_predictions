import numpy as np

cf_00 ={"kernel": np.array([[0, 1, 0],
                       [1, 0, 1],
                       [0, 1, 0]]),
      "stride": 2,
      "T_low" : -1,
       "T_hi" : 1,

    "secret_key": "imt_atlantique", # Select the blocks to watermark

    "message" : "a seed", # We provide only the seed, and the size of the watermark depends on the capacity in the image

    "original_image_path" : "images/Lena.tiff",

    "watermarked_image_path" : "results/Lena_watermarked.tiff",

    "recovered_image_path" : "results/Lena_recovered.tiff",

    "extracted_watermark_path": "results/watermark_extracted.npy"



}
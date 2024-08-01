import numpy as np

cf_00 = {"kernel": np.array([[0, 1 / 4, 0],
                             [1 / 4, 0, 1 / 4],
                             [0, 1 / 4, 0]]),
         "stride": 3,
         "T_hi": 0,

         "secret_key": "imt_atlantique",  # Select the blocks to watermark

         "message": "a seed",
         # We provide only the seed, and the size of the watermark depends on the capacity in the image

         "original_image_path": "images/Lena.tiff",

         "watermarked_image_path": "results/Lena_watermarked.tiff",

         "configs_path": "configs/config_logs.json"

         }

cf_01 = {"kernel": np.array([[0, 1 / 4, 0],
                             [1 / 4, 0, 1 / 4],
                             [0, 1 / 4, 0]]),
         "stride": 3,
         "T_hi": 0,

         "secret_key": "imt_atlantique",  # Select the blocks to watermark

         "message": "SessionID_UserID_SenderID_ReceiverID_TimeStamp_DataID",
         # We provide only the seed, and the size of the watermark depends on the capacity in the image

         "original_image_path": "images/modified_overflow.png",

         "watermarked_image_path": "results/Normal-1_watermarked.png",

         "configs_path": "configs/config_logs.json"

         }

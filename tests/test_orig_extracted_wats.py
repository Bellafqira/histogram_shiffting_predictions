import unittest

from watermarking.extract import extract_watermark
from configs import conf_wat00

class TestCompareWatermarks(unittest.TestCase):
    def test_extract(self):
        compare_wat(conf_wat00.cf_00)
        # Add your test assertions here

if __name__ == '__main__':
    unittest.main()

def compare_wat(conf):
    # I need to read the extracted watermark and get the len of the watermak to know the capacity of the scheme 
    
    # I do maybe a majority vote to get a watermak of size 256.  
    
    # Then generate the original watermark from the message 
   
    # at the end compare the watermarks using the BER 
    

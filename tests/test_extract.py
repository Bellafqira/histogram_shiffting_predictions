import unittest

from watermarking.extract import extract_watermark
from configs import conf_wat00

class TestExtractWatermark(unittest.TestCase):
    def test_extract(self):
        extract_watermark(conf_wat00.cf_00)
        # Add your test assertions here

if __name__ == '__main__':
    unittest.main()
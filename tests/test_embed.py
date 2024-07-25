import unittest
from watermarking.embed import embed_watermark
from configs import conf_wat00

class TestEmbedWatermark(unittest.TestCase):
    def test_embed(self):
        embed_watermark(conf_wat00.cf_00)
        # Add your test assertions here

if __name__ == '__main__':
    unittest.main()

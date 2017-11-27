import unittest
import os
from attitude_converter.attitude_provider import MappsReader, JuiceMex2Ker


class ReaderTests(unittest.TestCase):

    def test_juice_reader(self):
        filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'europa_fb_attitude.csv')
        bc_reader = MappsReader()
        bc_reader.read(filename)
        quats = bc_reader.quaternions
        bc2ck = JuiceMex2Ker()
        tmp_ck = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'test.ck')
        bc2ck.convert(quats, tmp_ck)
        self.assertTrue(os.path.exists(tmp_ck))
        self.assertEquals(os.path.getsize(tmp_ck), 8192)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ReaderTests)


def main():
    unittest.TextTestRunner(verbosity=1).run(suite())


if __name__ == '__main__':
    main()

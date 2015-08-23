#!/usr/bin/env python
import unittest
from wavfiles import WavFile, Silence, wav_iter, merge
import wave
import os


class WavFileTest(unittest.TestCase):

    def setUp(self):
        self.example = WavFile('./audio/F20150101120000.wav')

    def test_invalid_filenames(self):
        names = ['RVF1234567890.wav',
                 'N20194857389.wav',
                 'F2910594839992.wav'
                 '123456789012.wav']

        for x in names:
            with self.assertRaises(Exception):
                WavFile(x)

    def test_open(self):
        read = self.example.open()
        self.assertIsInstance(read, wave.Wave_read)
        read.close()

    def test_length(self):
        self.assertEqual(self.example.length(), 33.0)

    def test_read_all(self):
        # Should give bytes from `Wave_read`
        self.assertEqual(type(self.example.read_all()), bytes)


class SilenceTest(unittest.TestCase):

    def setUp(self):
        self.silence = Silence(3.0, 44100)

    def test_silence(self):
        self.assertEqual(self.silence.length(), 3.0)
        self.assertEqual(self.silence.framerate, 44100)
        # Should give bytearray, not bytes. Both will work with Wave_write.
        self.assertEqual(type(self.silence.read_all()), bytearray)


class MainTest(unittest.TestCase):

    def setUp(self):
        self.audiodir = './audio/'
        self.lname = self.audiodir + 'left.wav'
        self.rname = self.audiodir + 'right.wav'
        for x in [self.lname, self.rname]:
            if os.path.isfile(x):
                os.remove(x)

        self.files = sorted([WavFile(self.audiodir + f)
                             for f in os.listdir(self.audiodir) if f.endswith('.wav')],
                            key=lambda x: x.timestamp)
        self.left = [x for x in self.files if x.channel == 'L']
        self.right = [x for x in self.files if x.channel == 'R']

    def test_merge(self):
        merge(self.left, self.lname)
        self.assertTrue(os.path.isfile(self.lname))

        merge(self.right, self.rname)
        self.assertTrue(os.path.isfile(self.rname))

    def test_wav_iter(self):
        i = 0
        shouldbe = [WavFile, WavFile, Silence, WavFile,
                    Silence, WavFile, Silence, WavFile]
        for x in wav_iter(self.left):
            self.assertIsInstance(x, shouldbe[i])
            i += 1

if __name__ == '__main__':
    unittest.main()

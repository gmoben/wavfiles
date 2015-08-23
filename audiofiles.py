#!/usr/bin/env python3
import re
import wave
import os
from datetime import datetime


class WavFile:

    """
    Represents a WAV file and provides convenience methods for `wave`.
    """

    def __init__(self, location):
        matches = re.match(r'.+?([NF])(\d{14})\.wav$',
                           location)

        if not matches:
            raise Exception('Filename regex failed for %s' % location)

        (ch, timestamp) = matches.groups()

        if ch not in ('N', 'F'):
            raise Exception('Invalid/missing channel')

        self.location = location
        self.channel = 'L' if ch == 'N' else 'R'
        self.timestamp = datetime.strptime(timestamp, '%Y%m%d%H%M%S')

    def open(self, mode):
        return wave.open(self.location, mode)

    def length(self):
        f = self.open('r')
        return (f.getnframes() / f.getframerate()) / f.getnchannels()

    def read_all(self):
        f = self.open('r')
        frames = f.readframes(f.getnframes())
        return frames

    def __str__(self):
        return '%s [%s] [%s]' % (self.location, self.channel, self.timestamp)


class Silence:

    """
    Mono Silence
    """

    def __init__(self, length, framerate):
        self.length = length
        self.framerate = framerate

    def read_all(self):
        return bytearray([0] * int(self.framerate * self.length))


def wav_iter(files):
    i = 0
    yield files[i]
    # the next's delta time difference with prev
    while i < len(files) - 1:
        cur = files[i]
        next = files[i + 1]
        delta = (next.timestamp - cur.timestamp).seconds
        if cur.length() < delta:
            yield Silence(delta - cur.length(), cur.open('r').getframerate())
        yield next
        i = i + 1


def merge(wav_files, output_filename):
    # Get output params from first file
    params = wav_files[0].open('r').getparams()

    # Build output file
    output = wave.open(output_filename, 'w')
    output.setparams(params)

    # Sort by timestamp and merge to output in sequence
    wav_files = sorted(wav_files, key=lambda w: w.timestamp)
    for f in wav_iter(wav_files):
        output.writeframes(f.read_all())

    print('Merged to %s' % output_filename)

if __name__ == '__main__':
    audiodir = './audio/'
    left_fn = audiodir + 'left.wav'
    right_fn = audiodir + 'right.wav'

    # Remove any existing output
    for x in (left_fn, right_fn):
        if os.path.isfile(x):
            os.remove(x)

    # Create WavFile instances and separate left and right
    wav_files = [WavFile(audiodir + f)
                 for f in os.listdir(audiodir) if f.endswith('.wav')]
    left = [x for x in wav_files if x.channel == 'L']
    right = [x for x in wav_files if x.channel == 'R']

    # Ensure both sides are same length
    if not sum([x.length() for x in left]) == sum([x.length() for x in right]):
        raise Exception('Channels have unequal length')

    # Merge and save files
    merge(left, left_fn)
    merge(right, right_fn)

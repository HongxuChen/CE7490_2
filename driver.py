#!/usr/bin/env python

import os
import random
import string
import time

import config
import utils
from log_helper import get_logger, init_logger
from raid4 import RAID4
from raid5 import RAID5
from raid6 import RAID6


def gen_rnd_file(fname, size, content_type):
    """
    randomly generate data chunk
    :param fname: the name denoting the data
    :param size: the size of the data chunk
    :param content_type: can be 'text' or others; if it's 'text', make the chunk only contain ascii letters
    :return:
    """
    if content_type == 'text':
        # noinspection PyUnusedLocal
        content = ''.join([random.choice(string.ascii_letters) for i in xrange(size)])
    else:
        content = os.urandom(size)
    fpath = os.path.join(config.root, fname)
    if os.path.isfile(fpath):
        file_size = os.stat(fpath).st_size
        if file_size == size:
            get_logger().warning('fname={} with size={} exists'.format(fname, size))
            return
    get_logger().warning('generating fname={} with size={}'.format(fname, size))
    utils.write_content(fpath, content)


# noinspection PyUnusedLocal
def starter():
    """
    a starter function for random data generation
    :return:
    """
    if not os.path.isdir(config.root):
        os.mkdir(config.root)
    gen_rnd_file('data1', SIZE, 'text')
    gen_rnd_file('data2', SIZE, 'bin')


SIZE = 3276800
N_DISK = 8

if __name__ == '__main__':
    init_logger()
    starter()
    # for fname in ['data1', 'data2']:
    for fname in ['doge.png']:
        fpath = os.path.join(config.root, fname)
        with open(fpath, 'rb') as fh:
            content = fh.read()
        for raid_type in [RAID4, RAID5, RAID6]:
            raid = raid_type(10)
            start_time = time.time()
            raid.write(content, fname)
            print("{:10.4f}s during 'write' for raid={} against data={}, size={}".format(
                time.time() - start_time, raid.__class__.__name__, fname, SIZE))
            size = len(content)
            start_time = time.time()
            content_raid = raid.read(fname, size)
            print("{:10.4f}s during 'read'  for raid={} against data={}, size={}".format(
                time.time() - start_time, raid.__class__.__name__, fname, SIZE))
            assert content == content_raid
            # error_index = 2
            # raid.recover(fname, error_index)

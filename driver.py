#!/usr/bin/env python

import os
import random
import string

import config
from log_helper import get_logger, init_logger
from raid4 import RAID4
from raid6 import RAID6


def gen_rnd_file(fname, size, content_type):
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
    with open(fpath, 'wb') as fout:
        fout.write(content)


# noinspection PyUnusedLocal
def starter():
    if not os.path.isdir(config.root):
        os.mkdir(config.root)
    r4 = RAID4(config.N)
    r6 = RAID6(config.N)
    gen_rnd_file('data1', 3276800, 'text')
    gen_rnd_file('data2', 3276800, 'bin')


if __name__ == '__main__':
    init_logger()
    starter()
    fname = 'data2'
    fpath = os.path.join(config.root, fname)
    with open(fpath, 'rb') as fh:
        content = fh.read()
    r4 = RAID4(3)
    r4.write(content, fname)
    content_r4 = r4.read(fname)
    assert content == content_r4
    # counter = 0
    # for original, new in zip(content, content_r4):
    #     if original != new:
    #         print(original, new, counter)
    #         break

#!/usr/bin/env python
from __future__ import print_function

from itertools import repeat

import numpy as np

import utils
from log_helper import init_logger, get_logger
from raid import RAID


# noinspection PyPep8Naming,PyAttributeOutsideInit
class RAID4(RAID):
    def __init__(self, N):
        super(RAID4, self).__init__(N)

    def check(self, byte_nparray):
        res = np.bitwise_xor.reduce(byte_nparray)
        if np.count_nonzero(res) != 0:
            msg = 'xor of arrays not all zeros, res={}'.format(res)
            raise utils.ParityCheckError(msg)

    def read(self, fname):
        content_list = []
        for i in xrange(self.N):
            fpath = self.get_real_name(i, fname)
            content_list.append(self._contents(fpath))
        get_logger().info(content_list)
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # list of bytes (int) list
        byte_list = []
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.EOF] * (length - len(content))
            byte_list.append(current_str_list)
        # bytes array
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        self.check(byte_nparray)
        # read N-1
        data_nparray = byte_nparray[:-1]
        flat_list = filter(lambda ele: ele != self.EOF, data_nparray.ravel(1))
        flat_str_list = [chr(e) for e in flat_list]
        return ''.join(flat_str_list)

    def write(self, content, fname):
        # gen N-1 length empty list
        content_list = [[] for i in repeat(None, self.N - 1)]
        for i in xrange(len(content)):
            mod_i = i % (self.N - 1)
            content_list[mod_i].append(content[i])
        byte_list = []
        length = len(sorted(content_list, key=len, reverse=True)[0])
        # fill 0
        for content in content_list:
            current_str_list = [ord(s) for s in content] + [self.EOF] * (length - len(content))
            byte_list.append(current_str_list)
        byte_nparray = np.array(byte_list, dtype=self.BYTE_TYPE)
        get_logger().info('byte_array'.format(byte_nparray))
        # calculate parity and append
        parity = np.bitwise_xor.reduce(byte_nparray)
        assert parity.ndim == 1
        new_dim = parity.shape[0]
        parity.shape = (1, new_dim)
        write_array = np.concatenate([byte_nparray, parity])
        get_logger().info('write_array:\n{}'.format(write_array))
        # write N
        for j in range(self.N):
            fpath = self.get_real_name(j, fname)
            real_write_content = filter(lambda b: b >= 0, write_array[j])
            str_list = [chr(b) for b in real_write_content]
            content_i = ''.join(str_list)
            with open(fpath, 'wb') as fh:
                fh.write(content_i)


if __name__ == '__main__':
    init_logger()
    r4 = RAID4(4)
    data_fname = 'good.dat'
    # original_content = 'good_morning_sir'
    original_content = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'
    r4.write(original_content, data_fname)
    r4_content = r4.read(data_fname)
    print(r4_content.__repr__())
    assert r4_content == original_content

import os
import sys
import time
import zlib

import multiprocessing as mp

ENCRYPT_KEY = 0xA8


def encrypt_or_decrypt(enc, file_name, processed_filename):
    current_time = time.time()
    print('open file binary {0}'.format(file_name))
    # 打开文件，得到文件流
    data = open(file_name, "rb").read()
    print('open file time = {0} second'.format(time.time() - current_time))
    current_time = time.time()
    # 如果不是加密文件，那就是解密。解密前需要先把文件gzip解压处理
    if not enc:
        data = zlib.decompress(data)
        print('decompress time = {0} second'.format(time.time() - current_time))
        current_time = time.time()
    # 解压后再从bytes转换成bytearray。方便将byte和key进行'异或'加密或者解密
    data = bytearray(data)
    for i in range(len(data)):
        data[i] = data[i] ^ ENCRYPT_KEY

    print('{0} time = {1} second'.format('encrypt' if enc else 'decrypt', time.time() - current_time))
    current_time = time.time()
    # 如果是加密文件，则需要在异或后进行bytes的压缩处理
    if enc:
        data = zlib.compress(data)
        print('compress time = {0} second'.format(time.time() - current_time))
        current_time = time.time()
    # 随后将处理好的bytes流写入到文件中
    open(processed_filename, "wb").write(data)
    print('save file = {0} time = {1} second'.format(processed_filename, time.time() - current_time))


def folder_enc_dec(is_enc: bool, folder_path: str, name: str):
    filename = os.path.join(os.path.abspath(folder_path), name)
    if os.path.isfile(filename):
        if filename.endswith('.enc') and is_enc:
            return
        if not filename.endswith('.enc') and not is_enc:
            return
        new_file_name = filename + '.enc' if is_enc else filename.replace('.enc', '')
        encrypt_or_decrypt(is_enc, filename, new_file_name)
        os.remove(filename)


if __name__ == '__main__':
    # sys.argv 命令行参数列表
    is_encrypt = sys.argv[1] == 'encrypt'
    if sys.argv[2] == 'file':
        if len(sys.argv) > 5:
            try:
                key = int(sys.argv[5])
                if key >= 256 or key < 0:
                    raise ValueError('key must be less than 256 and greater than or equal to 0')
                ENCRYPT_KEY = key
            except ValueError as e:
                print('Encrypt key Incorrect format,message : {0}, use normal key {1}'.format(e, ENCRYPT_KEY))
        encrypt_or_decrypt(is_encrypt, sys.argv[3], sys.argv[4])
    elif sys.argv[2] == 'folder':
        folder = sys.argv[3]
        if len(sys.argv) > 4:
            try:
                key = int(sys.argv[4])
                if key >= 256 or key < 0:
                    raise ValueError('key must be less than 256 and greater than or equal to 0')
                ENCRYPT_KEY = key
            except ValueError as e:
                print('Encrypt key Incorrect format,message : {0}, use normal key {1}'.format(e, ENCRYPT_KEY))
        file_names = os.listdir(folder)
        for index in range(len(file_names)):
            process = mp.Process(target=folder_enc_dec, args=(is_encrypt, folder, file_names[index]))
            process.start()

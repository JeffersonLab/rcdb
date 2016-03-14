import hashlib
import base64


def get_file_hash(afile, hasher, block_size=65536):
    """Gets checksumm of the file using a given hasher"""
    buf = afile.read(block_size)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(block_size)
    return hasher.digest()


def get_file_sha256(fname):
    """Gets  base64 encoded sha256 hash encoded with base64

    note, base64 is to make it readable
    http://stackoverflow.com/questions/9660079/why-base64-a-sha1-sha256-hash
    """
    with open(fname, 'rb') as afile:
        return base64.b64encode(get_file_hash(afile, hashlib.sha256()))


def get_string_sha256(str_to_convert):
    """Returns base64 encoded sha256 of the string converting it to byte array

    The function is done so, that if you encode text file by get_file_sha256
    and contents of the file with this function you'll get the same results

    :param str_to_convert:
    :return:
    """
    hasher = hashlib.sha256()
    hasher.update(bytearray(str_to_convert.encode('ascii')))
    return base64.b64encode(hasher.digest())
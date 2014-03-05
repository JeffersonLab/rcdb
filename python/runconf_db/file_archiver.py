import hashlib
import base64


def get_file_sha256(fname):
    """Gets sha256 hash encoded with base64"""

    block_size = 65536
    with open(fname, 'rb') as file:
        hasher = hashlib.sha256()
        buf = file.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(block_size)
        return base64.b64encode(hasher.digest())





def add_file(run_num, file_path):
    pass


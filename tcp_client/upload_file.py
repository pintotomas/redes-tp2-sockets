from utils.tcp_connection import TCPConnection
from utils.op_codes import OP_CODES


def _read_file(src):
    f = open(src, 'rb')
    content = f.read()
    f.close()

    return content


def upload_file(server_address, src, name):
    try:
        content = _read_file(src)
        connection = TCPConnection(host=server_address[0],
                                   port=server_address[1])

        connection.sendNumber(OP_CODES['upload'])
        connection.sendString(name, encode=True)
        connection.sendString(content)
    except FileNotFoundError:
        print('File not found!')

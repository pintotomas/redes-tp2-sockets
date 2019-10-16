from utils.tcp_connection import TCPConnection
from utils.op_codes import OP_CODES


def _read_file(src):
    f = open(src)
    content = f.read()
    f.close()

    return content


def upload_file(server_address, src, name):
    content = _read_file(src)
    connection = TCPConnection(host=server_address[0],
                               port=server_address[1])

    connection.sendNumber(OP_CODES['upload'])
    connection.sendString(name)
    connection.sendString(content)

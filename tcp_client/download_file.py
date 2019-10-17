from utils.tcp_connection import TCPConnection
from utils.op_codes import OP_CODES


def _save_file(dst, content):
    f = open(dst, 'wb')
    f.write(content)
    f.close()


def download_file(server_address, name, dst):
    connection = TCPConnection(host=server_address[0],
                               port=server_address[1])

    connection.sendNumber(OP_CODES['download'])
    connection.sendString(name, encode=True)
    content = connection.recvString()

    _save_file(dst, content)

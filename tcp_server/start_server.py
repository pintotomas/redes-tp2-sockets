from utils.tcp_connection import TCPConnectionHandler
from utils.op_codes import OP_CODES


def _handle_upload(connection, storage_dir):
    name = connection.recvString()
    content = connection.recvString()

    with open('{}/{}'.format(storage_dir, name), 'w') as f:
        f.write(content)


def _handle_download(connection, storage_dir):
    name = connection.recvString()

    with open('{}/{}'.format(storage_dir, name), 'r') as f:
        content = f.read()
    connection.sendString(content)


def start_server(server_address, storage_dir):
    handler = TCPConnectionHandler(server_address[0],
                                   server_address[1])

    while True:
        connection = handler.accept()
        op_code = connection.recvNumber()
        if op_code == OP_CODES['upload']:
            _handle_upload(connection, storage_dir)
        elif op_code == OP_CODES['download']:
            _handle_download(connection, storage_dir)
        else:
            raise RuntimeError('Invalid operation.')

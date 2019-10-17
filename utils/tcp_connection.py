import socket
import struct


class TCPConnectionHandler:
    LISTEN_QUEUE_SIZE = 3

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(self.LISTEN_QUEUE_SIZE)

    def __del__(self):
        self.sock.close()

    def accept(self):
        newSocket, _address = self.sock.accept()
        return TCPConnection(sock=newSocket)


class TCPConnection:
    PACK_FORMAT = '!i'
    RECV_INT_SIZE = 4
    RECV_CHUNK_SIZE = 1024

    def __init__(self, host=None, port=None, sock=None):
        if sock:
            self.sock = sock
        else:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)
            self.sock.connect((host, port))

    def __del__(self):
        self.sock.close()

    def _sendData(self, data):
        size = len(data)
        totalSent = 0

        while totalSent < size:
            sent = self.sock.send(data[totalSent:])
            if sent == 0:
                raise RuntimeError('Unable to send data.')

            totalSent += sent

        return totalSent

    def _recvData(self, length):
        data = []
        totalRecv = 0

        while totalRecv < length:
            partialData = self.sock.recv(min(self.RECV_CHUNK_SIZE,
                                             length - totalRecv))
            if len(partialData) == 0:
                raise RuntimeError('Unable to receive data.')

            totalRecv += len(partialData)
            data.append(partialData)

        return b''.join(data)

    def sendNumber(self, data):
        packedData = struct.pack(self.PACK_FORMAT, data)
        return self._sendData(packedData)

    def sendString(self, data, encode=False):
        if encode:
            data = data.encode()

        sent = 0
        sent += self.sendNumber(len(data))
        sent += self._sendData(data)
        return sent

    def recvNumber(self):
        return struct.unpack(self.PACK_FORMAT,
                             self._recvData(self.RECV_INT_SIZE))[0]

    def recvString(self, decode=False):
        length = self.recvNumber()
        data = self._recvData(length)
        return data.decode() if decode else data

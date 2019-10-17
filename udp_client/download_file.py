import socket
import pickle

DOWNLOAD = 2
UPLOAD = 1
CHUNK_SIZE = 1980 #32 bytes para otras cosas #6 bytes para el numero de chunk

def download_file(server_address, name, dst):
  # TODO: Implementar UDP download_file client
  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))
  own_address = ("127.0.0.1", 8081)
  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(own_address)

  #Enviar tambien informacion del own address
  requested_file_data = {"name": name,
              "OP": DOWNLOAD}

  sock.sendto(pickle.dumps(requested_file_data), server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)
  #Aca se queda infinitamente esperando una respuesta del server


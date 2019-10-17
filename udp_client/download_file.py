from socket import *
import pickle
from .udp_buffer import UdpBuffer
DOWNLOAD = 2
UPLOAD = 1
CHUNK_SIZE = 1980 #32 bytes para otras cosas #6 bytes para el numero de chunk

def download_file(server_address, name, dst):
  # TODO: Implementar UDP download_file client
  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))
  own_address = ("127.0.0.1", 8081)
  # Create socket and connect to server
  sock = socket(AF_INET, SOCK_DGRAM)
  sock.bind(own_address)

  #Enviar tambien informacion del own address
  requested_file_data = {"name": name,
              "OP": DOWNLOAD}

  sock.sendto(pickle.dumps(requested_file_data), server_address)

  start_signal_obtained = False
  sock.settimeout(20)
  while not(start_signal_obtained):
  	try:
  		data, addr = sock.recvfrom(CHUNK_SIZE)
  		start_signal_obtained = True
  	except timeout:
  		#Vuelvo a enviar la solicitud del archivo que busco
  		sock.sendto(pickle.dumps(requested_file_data), server_address)

  data = pickle.loads(data)
  if data["signal"] == "start":
    udp_buffer = UdpBuffer()
    data, addr = sock.recvfrom(CHUNK_SIZE)
    data = pickle.loads(data)
    print("Receiving {} bytes in {} chunks".format(data["size"], data["total_chunks"]))

  elif data["signal"] == "file_not_found":
  	return
  #Aca se queda infinitamente esperando una respuesta del server


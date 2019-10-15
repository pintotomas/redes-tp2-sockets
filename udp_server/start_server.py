import argparse
import socket
import time
import json 

def get_timestamp():
  return int(round(time.time()*1000))

CHUNK_SIZE = 1024

def start_server(server_address, storage_dir):
  #TO DO
  # - Guardar el archivo correctamente
  # - Avisar al cliente si no se recibieron todos los datos

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(server_address)
  sock.settimeout(4)

  while True:
    data, addr = sock.recvfrom(CHUNK_SIZE)
    size = int(data.decode())
    print("Incoming file with size {} from {}".format(size, addr))

    filename = "./file-{}.bin".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    sock.sendto(b'start', addr)

    while bytes_received < size:

      #infinito si no se recibe la cantidad de bytes correctos
      #podemos probar aca despues de un cierto tiempo mandar 
      #sock.sendto(str(bytes_received).encode(),addr)
      #y despues el cliente que se encargue de mandar los bytes restantes
      #No estoy seguro el tema del orden en que esto esta recibiendo los datos

      data, addr = sock.recvfrom(CHUNK_SIZE)

      data = json.loads(data.decode())
      chunk_number = data.get("chunk_number")
      chunk = data.get("chunk").encode()

      bytes_received += len(chunk)
      f.write(chunk)

    print("Received file {}".format(filename))

    # Send number of bytes received
    sock.sendto(str(bytes_received).encode(),addr)

    f.close()

  sock.close()

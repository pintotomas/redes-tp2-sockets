import argparse
import socket
import time
import json 
from .udp_buffer import UdpBuffer

def get_timestamp():
  return int(round(time.time()*1000))

CHUNK_SIZE = 2048

def start_server(server_address, storage_dir):
  #TO DO
  # - Guardar el archivo correctamente
  # - Avisar al cliente si no se recibieron todos los datos

  #TO DO: Deberia haber un buffer por cliente
  udp_buffer = UdpBuffer() 

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
    chunks_received = 0
    while bytes_received < size:
      data, addr = sock.recvfrom(CHUNK_SIZE)

      data = json.loads(data.decode())
      chunk_number = data.get("chunk_number")
      chunk = data.get("chunk").encode()
      
      udp_buffer.add_chunk(chunk_number, chunk)
      bytes_received += len(chunk)

      #chunks_received += 1
      #print("Chunks received: "+str(chunks_received))



      #f.write(chunk)

    print("Received file {}".format(filename))

    # Send number of bytes received
    sock.sendto(str(bytes_received).encode(),addr)

    f.close()

  sock.close()

def save_file(filename, buffer, chunks_quantity):
  return
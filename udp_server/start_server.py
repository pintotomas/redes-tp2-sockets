import argparse
from socket import *
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

  sock = socket(AF_INET, SOCK_DGRAM)
  sock.bind(server_address)
  sock.settimeout(4)

  while True:
    data, addr = sock.recvfrom(CHUNK_SIZE)
    #size = int(data.decode())
    data = json.loads(data.decode())
    size = int(data["size"])
    total_chunks = int(data["total_chunks"])
    print("Incoming file with size {} with {} chunks from {}".format(size, total_chunks, addr))

    filename = "./file-{}.bin".format(get_timestamp())
    f = open(filename, "wb")
    bytes_received = 0

    sock.sendto(b'start', addr)

    while bytes_received < size:
      try:
          data, addr = sock.recvfrom(CHUNK_SIZE)
          data = json.loads(data.decode())
          chunk_number = data.get("chunk_number")
          chunk = data.get("chunk").encode()
          udp_buffer.add_chunk(chunk_number, chunk)
          bytes_received += len(chunk)
          
      except timeout:
        for actual_chunk_number in range(total_chunks):

          actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
          if actual_chunk != -1:
            continue
          else:
            received_missing_data = False
            timeouts = 0
            while not(received_missing_data):
              try:
                data = {"get_chunk": actual_chunk_number}
                sock.sendto(json.dumps(data).encode(), addr)
                data, addr = sock.recvfrom(CHUNK_SIZE)
                data = json.loads(data.decode())
                chunk_number = data.get("chunk_number")
                chunk = data.get("chunk").encode()
                if chunk_number == actual_chunk_number:
                  udp_buffer.add_chunk(chunk_number, chunk)
                  received_missing_data = True

              except timeout:
                timeouts += 1

            data = json.loads(data.decode())
            chunk = data.get("chunk").encode()
            bytes_received += len(chunk)

    for actual_chunk_number in range(total_chunks):
      actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
      f.write(actual_chunk)

    print("Received file {}".format(filename))

    # Send number of bytes received
    data = {"bytes_received": bytes_received}
    sock.sendto(json.dumps(data).encode(),addr)

    f.close()

  sock.close()

def save_file(filename, buffer, chunks_quantity):
  return
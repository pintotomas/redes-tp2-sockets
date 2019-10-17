import argparse
from socket import *
import time
import pickle
from .udp_buffer import UdpBuffer
import os
import math

def get_timestamp():
  return int(round(time.time()*1000))

CHUNK_SIZE = 2048
TRANSFER_CHUNK_SIZE = 1980
DOWNLOAD = 2
UPLOAD = 1

def start_server(server_address, storage_dir):
  #TO DO
  # - Guardar el archivo correctamente
  # - Avisar al cliente si no se recibieron todos los datos

  #TO DO: Deberia haber un buffer por cliente
  udp_buffer = UdpBuffer() 
  sock = socket(AF_INET, SOCK_DGRAM)
  sock.bind(server_address)
  sock.settimeout(3)

  while True:
    try:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      data = pickle.loads(data)
      operation_code = int(data["OP"])
      
    except timeout:
      #revivo al server
      sock.settimeout(3)
      continue
    if (operation_code == UPLOAD):
      #ACA CADA VEZ QUE RECIBA DATA, CHEQUEAR QUE EL CODIGO SEA UPLOAD, Y SI NO ES, DESCARTARLO
      sock.sendto(b'start', addr)
      size = int(data["size"])
      total_chunks = int(data["total_chunks"])
      print("Incoming file with size {} with {} chunks from {}".format(size, total_chunks, addr))

      filename = "./file-{}.bin".format(get_timestamp())
      f = open(filename, "wb")
      bytes_received = 0
      while bytes_received < size:
        try:
            data, addr = sock.recvfrom(CHUNK_SIZE)
            data = pickle.loads(data)
            chunk_number = data.get("chunk_no")
            chunk = data.get("chunk")
            udp_buffer.add_chunk(chunk_number, chunk)
            bytes_received += len(chunk)
            
        except timeout:

          #Caso MUY extraño: A veces me pasa que no se escribe bien la cantidad de bytes recibidos en bytes_received
          #Pero se guardaron en el buffer
          if udp_buffer.size() == total_chunks:
            break
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
                  sock.sendto(pickle.dumps(data), addr)
                  data, addr = sock.recvfrom(CHUNK_SIZE)
                  data = pickle.loads(data)
                  chunk_number = data.get("chunk_no")
                  chunk = data.get("chunk")
                  if chunk_number == actual_chunk_number:
                    udp_buffer.add_chunk(chunk_number, chunk)
                    received_missing_data = True

                except timeout:
                  timeouts += 1

              bytes_received += len(chunk)

      for actual_chunk_number in range(total_chunks):

        actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
        f.write(actual_chunk)

      print("Received file {}".format(filename))

      # Send number of bytes received
      data = {"bytes_received": bytes_received}
      sock.sendto(pickle.dumps(data), addr)

      f.close()

    elif (operation_code == DOWNLOAD):
      file_name = data["name"]
      file_path = storage_dir+"/"+file_name
      file_exists = os.path.exists(file_path)
      data = {}
      if (file_exists):
        data["signal"] = "start"
      else:
        data["signal"] = "file_not_found"

      sock.sendto(pickle.dumps(data), addr)

      if data["signal"] == "file_not_found":
        continue

  sock.close()

def save_file(filename, buffer, chunks_quantity):
  return
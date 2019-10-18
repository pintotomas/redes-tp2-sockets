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
  if not os.path.exists(storage_dir):
      os.makedirs(storage_dir)
  udp_buffer = UdpBuffer()
  sock = socket(AF_INET, SOCK_DGRAM)
  sock.bind(server_address)
  sock.settimeout(3)
  CURRENT_WORKING_ADDRESS = None

  while True:
    try:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      CURRENT_WORKING_ADDRESS = addr
      data = pickle.loads(data)
      operation_code = int(data["OP"])

    except timeout:
      #revivo al server
      sock.settimeout(3)
      continue
    if (operation_code == UPLOAD):
      #ACA CADA VEZ QUE RECIBA DATA, CHEQUEAR QUE EL CODIGO SEA UPLOAD, Y SI NO ES, DESCARTARLO
      signal_data = {"signal": "start"}
      sock.sendto(pickle.dumps(signal_data), CURRENT_WORKING_ADDRESS)
      size = int(data["size"])
      total_chunks = int(data["total_chunks"])
      name = data["name"]
      print("Incoming file with size {} with {} chunks from {}".format(size, total_chunks, addr))

      filename = "{}/{}".format(storage_dir, name)
      

      bytes_received = 0
      continue_upload = True
      while bytes_received < size:
        if not(continue_upload):
          break
        try:
            data, addr = sock.recvfrom(CHUNK_SIZE)
            if (addr != CURRENT_WORKING_ADDRESS):
              continue
              
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
            if not(continue_upload):
              break
            actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
            if actual_chunk != -1:
              continue

            else:
              received_missing_data = False
              timeouts = 0

              while not(received_missing_data):
                try:
                  if(timeouts > 40):
                    #10 timeouts son 30 segundos (timeout setteado en 3)
                    #despues de eso, suponemos que murio el cliente y reseteamos esto
                    print("Client does not respond, stopping upload..")
                    CURRENT_WORKING_ADDRESS = None
                    continue_upload = False
                    break
                  data = {"get_chunk": actual_chunk_number}
                  sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)
                  data, addr = sock.recvfrom(CHUNK_SIZE)
                  if (addr != CURRENT_WORKING_ADDRESS):
                    addr = CURRENT_WORKING_ADDRESS
                    continue
                  data = pickle.loads(data)
                  chunk_number = data.get("chunk_no")
                  chunk = data.get("chunk")
                  if chunk_number == actual_chunk_number:
                    udp_buffer.add_chunk(chunk_number, chunk)
                    bytes_received += len(chunk)
                    received_missing_data = True

                except timeout:
                  timeouts += 1

              
      if (continue_upload):
        f = open(filename, "wb")
        for actual_chunk_number in range(total_chunks):

          actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
          f.write(actual_chunk)

        print("Received file {}".format(filename))

        # Send number of bytes received
        data = {"bytes_received": bytes_received}
        sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)
        CURRENT_WORKING_ADDRESS = None
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

      sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)

      if data["signal"] == "file_not_found":
        continue
      f = open(file_path, "rb")
      f.seek(0, os.SEEK_END)
      size = f.tell()
      total_chunks = math.ceil(size/TRANSFER_CHUNK_SIZE)
      f.seek(0, os.SEEK_SET)
      print("Sending {} bytes in {} chunks".format(size, total_chunks))
      data = {"size": size,
             "total_chunks": total_chunks}

      sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)

      chunk_number = 0

      while True:
        chunk = f.read(TRANSFER_CHUNK_SIZE)

        if not chunk:
          break
        data = { "chunk_no": chunk_number, "chunk": chunk }
        sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)
        chunk_number += 1

      client_received_file = False
      sock.settimeout(None)
      while not(client_received_file):
        data, addr = sock.recvfrom(CHUNK_SIZE)
        if (addr != CURRENT_WORKING_ADDRESS):
          continue
        data = pickle.loads(data)
        if "get_chunk" in data:
          chunk_number = data["get_chunk"]
          file_position = (chunk_number)*TRANSFER_CHUNK_SIZE
          f.seek(file_position)
          chunk = f.read(TRANSFER_CHUNK_SIZE)
          data = { "chunk_no": chunk_number,
                 "chunk": chunk,
                 "OP": UPLOAD }
          sock.sendto(pickle.dumps(data), CURRENT_WORKING_ADDRESS)
        elif "bytes_received" in data:
          num_bytes = data["bytes_received"]
          print("Client received {} bytes".format(num_bytes))
          client_received_file = True
      CURRENT_WORKING_ADDRESS = None

  sock.close()
  

def save_file(filename, buffer, chunks_quantity):
  return
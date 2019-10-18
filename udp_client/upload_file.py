import os
import argparse
import socket
import pickle
import math
import pathlib

DOWNLOAD = 2
UPLOAD = 1
CHUNK_SIZE = 1980 #32 bytes para otras cosas #6 bytes para el numero de chunk

def upload_file(server_address, src, name):

  own_address = ("127.0.0.1", 8081)
  try:
    f = open(src, "rb")
  except FileNotFoundError:
    print('There was an error opening the file!')
    return
      
  f.seek(0, os.SEEK_END)
  size = f.tell()
  total_chunks = math.ceil(size/CHUNK_SIZE)
  f.seek(0, os.SEEK_SET)
  

  # Create socket and connect to server

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  binded = False
  addresses = ["127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5"]
  ip = 0
  port = 8081
  while not(binded):
    try:
      own_address = (addresses[ip], port)
      sock.bind(own_address)
      binded = True
    except OSError:
      ip += 1
  file_data = {"size": str(size),
              "total_chunks": str(total_chunks),
              "OP": UPLOAD,
              "name": name}

  sock.sendto(pickle.dumps(file_data), server_address)
  start_signal_obtained = False
  sock.settimeout(20)
  while not(start_signal_obtained):
    try:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      start_signal_obtained = True
    except socket.timeout:
      #Vuelvo a enviar la solicitud del archivo que busco
      sock.sendto(pickle.dumps(file_data), server_address)

  data = pickle.loads(data)
  if data["signal"] != "start":
    print("There was an error on the server")
    return exit(1)

  print("Sending {} bytes in {} chunks from {}".format(size, total_chunks, src))
  #contador para que el server sepa que chunks va recibiendo
  chunk_number = 0

  while True:
    chunk = f.read(CHUNK_SIZE)

    if not chunk:
      break
    data = { "chunk_no": chunk_number,
             "chunk": chunk, #.decode('utf-8'),
             "OP": UPLOAD }
    sock.sendto(pickle.dumps(data), server_address)#.encode(), server_address)
    chunk_number += 1

  # Recv amount of data received by the server
  timeouts = 0
  while True:
    if(timeouts > 10):
      print("No more responses from server, stopping upload.")
      break
    try:
      data, addr = sock.recvfrom(CHUNK_SIZE)
      data = pickle.loads(data)
      if "get_chunk" in data:
        chunk_number = data["get_chunk"]
        file_position = (chunk_number)*CHUNK_SIZE
        f.seek(file_position)
        chunk = f.read(CHUNK_SIZE)
        data = { "chunk_no": chunk_number,
               "chunk": chunk,
               "OP": UPLOAD }
        sock.sendto(pickle.dumps(data), server_address)
      elif "bytes_received" in data:
        num_bytes = data["bytes_received"]
        print("Server received {} bytes".format(num_bytes))
        break
    except socket.timeout:
      timeouts += 1
      continue

  f.close()
  sock.close()

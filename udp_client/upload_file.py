import os
import argparse
import socket
import pickle
import math

DOWNLOAD = 2
UPLOAD = 1
CHUNK_SIZE = 1980 #32 bytes para otras cosas #6 bytes para el numero de chunk

def upload_file(server_address, src, name):

  own_address = ("127.0.0.1", 8081)

  f = open(src, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  total_chunks = math.ceil(size/CHUNK_SIZE)
  f.seek(0, os.SEEK_SET)
  print("Sending {} bytes in {} chunks from {}".format(size, total_chunks, src))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(own_address)

  file_data = {"size": str(size),
              "total_chunks": str(total_chunks),
              "OP": UPLOAD}

  sock.sendto(pickle.dumps(file_data), server_address)
  signal, addr = sock.recvfrom(CHUNK_SIZE)

  if signal.decode() != "start":
    print("There was an error on the server")
    return exit(1)

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
  while True:
    data, addr = sock.recvfrom(CHUNK_SIZE)
    data = pickle.loads(data)
    if "get_chunk" in data:
      chunk_number = data["get_chunk"]
      file_position = (chunk_number-1)*CHUNK_SIZE 
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

  f.close()
  sock.close()

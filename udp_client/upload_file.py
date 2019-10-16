import os
import argparse
import socket
import json

CHUNK_SIZE = 1990 #32 bytes para otras cosas #6 bytes para el numero de chunk

def upload_file(server_address, src, name):

  own_address = ("127.0.0.1", 8081)

  f = open(src, "rb")
  f.seek(0, os.SEEK_END)
  size = f.tell()
  f.seek(0, os.SEEK_SET)
  total_chunks = size/CHUNK_SIZE
  print("Sending {} bytes from {}".format(size, src))

  # Create socket and connect to server
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(own_address)

  sock.sendto(str(size).encode(), server_address)
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
    data = {"chunk_number": chunk_number,
            "chunk": chunk.decode('utf-8'),
            "OP": "upload_chunk"}
    sock.sendto(json.dumps(data).encode(), server_address)
    chunk_number += 1
    #chunks_sent += 1

  #print("Chunks sent: "+str(chunks_sent))
  # Recv amount of data received by the server
  
  num_bytes, addr = sock.recvfrom(CHUNK_SIZE)

  print("Server received {} bytes".format(num_bytes.decode()))

  f.close()
  sock.close()

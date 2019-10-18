from socket import *
import pickle
from .udp_buffer import UdpBuffer

DOWNLOAD = 2
UPLOAD = 1
CHUNK_SIZE = 2048 #32 bytes para otras cosas #6 bytes para el numero de chunk

def download_file(server_address, name, dst):
  # TODO: Implementar UDP download_file client
  print('UDP: download_file({}, {}, {})'.format(server_address, name, dst))
  # Create socket and connect to server
  sock = socket(AF_INET, SOCK_DGRAM)
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
    size = data["size"]
    total_chunks = data["total_chunks"]
    print("Receiving {} bytes in {} chunks".format(size, total_chunks))
    bytes_received = 0
    sock.settimeout(3)
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
                sock.sendto(pickle.dumps(data), server_address)
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

    f = open(dst, 'wb')
    for actual_chunk_number in range(total_chunks):
        actual_chunk = udp_buffer.get_chunk(actual_chunk_number)
        f.write(actual_chunk)
    f.close()
    print("Received file {}".format(dst))
    data = {"bytes_received": size}
    sock.sendto(pickle.dumps(data), server_address)

  elif data["signal"] == "file_not_found":
    print("File not found!")
    return
  #Aca se queda infinitamente esperando una respuesta del server


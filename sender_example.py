# -*- coding: utf-8 -*-
import socket
import sys
import os

if len(sys.argv) != 4:
    print "python sender.py [IPADDRESS] [PORTNUMBER] [FILENAME]"
    sys.exit()

# armamos el socket
the_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# obtenemos el puerto y la IP
Server_IP = sys.argv[1]
Server_Port = int(sys.argv[2])

# establecemos parámetros
buf = 1024
address = (Server_IP,Server_Port)
seq = 0
ack = 0
# obtenemos los parámetros del archivo a enviar
file_name=sys.argv[3]
total_size = os.path.getsize(file_name)
current_size = 0
percent = round(0,2)

# abrimos el archivo
sending_file = open(file_name,"rb")

# 'codificamos' el header
data = str(file_name) + "|||" + str(total_size) + "|||" + str(seq)

# while para enviar datos
while True:
    # mandamos los datos donde corresponde
    the_socket.sendto(data,address)

    # actualizamos el número de secuencia
    seq = (seq + 1) % 2

    # seteamos un timeout (bloqueamos el socket después de 0.5s)
    the_socket.settimeout(0.5)

    # contador de intentos
    try_counter = 0

    # vemos que llegue el ACK
    while True:
        try:
            # si en 10 intentos no funciona, salimos
            if try_counter == 10:
                print "error"
                break

            # obtenemos la respuesta (estamos esperando un ACK)
            ack, address = the_socket.recvfrom(buf)

            # si recibimos lo que esperabamos, actualizamos cómo va el envío
            if (str(ack) == str(seq)):
                print str(current_size) + " / " + str(total_size) + "(current size / total size), " + str(percent) + "%"

                # y pasamos a actualizar los parametros en (**)
                break

            # si no, seguimos esperando el ack
            else:
                print "ack is not equal to seq"

        except:
            # si ocurre un error aumentamos avisamos y aumentamos el contador
            try_counter += 1
            print "timed out"
            the_socket.sendto(data,address)

    # si en 10 intentos no funciona, salimos
    if try_counter == 10:
        break

    # (**):
    data = sending_file.read(buf-1)
    current_size += len(data)
    percent = round(float(current_size) / float(total_size) * 100,2)

    # si no hay datos mandamos un string vacío y dejamos de enviar cosas
    if not data:
        the_socket.sendto("",address)
        break

    # actualizamos los datos a enviar
    data += str(seq)

# cerramos conexión y archivo
the_socket.close()
sending_file.close()
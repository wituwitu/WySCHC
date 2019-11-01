# -*- coding: utf-8 -*-
import socket
import sys

if len(sys.argv) != 2:
    print "python receiver.py [PORTNUMBER]"

SW_IP = ""
SW_PORT = int(sys.argv[1])
# armamos el socket
the_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# asociamos el socket a la dirección y el puerto especificados
the_socket.bind((SW_IP,SW_PORT))

# establecemos parámetros
buf = 1024
ack = 0
current_size = 0
percent = round(0,2)
can_receive = True

# partimos con la secuencia inicial: aquí abrimos el archivo a descargar
while True:
    # recibimos un string con los datos y la dirección del socket que mandó los datos
    data, address = the_socket.recvfrom(buf)

    if data:
        # separamos los datos recibidos
        (file_name, total_size, seq) = data.split("|||")

        # si recibimos los datos que esperabamos guardamos el archivo
        if str(seq) == str(ack):
            downloading_file = open("received_" + file_name,"wb")
            # mostramos el avance
            print str(current_size) + " / " + str(total_size) + " (current size / total size), " + str(percent) + "%"
            # actualizamos el ack
            ack = (ack + 1) % 2
            # enviamos el ack
            the_socket.sendto(str(ack),address)
            break

# seteamos un timeout (bloqueamos el socket después de 0.5s)
the_socket.settimeout(0.5)

# contador de intentos
try_counter = 0

# continuamos con la secuencia de descarga
while True:
    if can_receive:
        try:
            # si en 10 intentos no funciona, salimos
            if try_counter == 10:
                print "error"
                break

            data, address = the_socket.recvfrom(buf)

            if not data:
                break

            seq = data[len(data)-1]
            data = data[0:len(data)-1]

            # si no es lo que esperabamos, descartamos
            if (str(ack) != str(seq)):
                print "seq is not equal to ack"
                continue
            # si es, el socket queda tomado
            can_receive = False

        except:
            # si ocurre un error aumentamos avisamos y aumentamos el contador
            try_counter += 1
            print "timed out"
            the_socket.sendto(str(ack),address)


    if not can_receive:
        # escribimos los datos en el archivo que abrimos antes
        downloading_file.write(data)
        # actualizamos los parámetros
        current_size += len(data)
        percent = round(float(current_size) / float(total_size) * 100,2)
        print str(current_size) + " / " + str(total_size) + " (current size / total size), "  + str(percent) + "%"
        ack = (ack + 1) % 2
        try_counter = 0
        the_socket.sendto(str(ack),address)
        # ahora podemos volver a recibir cosas
        can_receive = True

# cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print "File Downloaded"
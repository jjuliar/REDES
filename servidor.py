# Python program to implement server side of chat room.
import socket
import select
import sys
from _thread import *
import tqdm
import json
import os
 
# Abre JSON
with open(os.path.join(sys.path[0], "database.json")) as f:
  users = json.load(f)

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# checks whether sufficient arguments have been provided
serverName = '127.0.0.1'
serverPort = 5000

server.bind((serverName,serverPort))

server.listen(100)

list_of_clients = []
loggedUsers = {}

def clientthread(conn, addr):
	message = 'Bem vindo! Realize o login'
	thisUser = ''
	# sends a message to the client whose user object is conn
	conn.send( message.encode())

	while True:
			try:
				message = conn.recv(BUFFER_SIZE)
				message = message.decode()

				if message:
					if message.startswith("<Login>"):
						file_info = message.split("|")
						nickname = file_info[1]
						password = file_info[2]

						try:
							if nickname in users:
								if users[nickname]['password'] == password:
									print('Usuário ' + nickname + ' logou')
									loggedUsers[nickname] = conn
									thisUser = nickname
									conn.send(f"<Login>|True|Login realizado com sucesso!".encode())
									message_to_send = thisUser + " entrou."
									broadcast(message_to_send, conn)
								else:
									conn.send(f"<Login>|False|Usuário ou senha inválidos.".encode())
							else:
								conn.send(f"<Login>|False|Usuário ou senha inválidos.".encode())
						except:
							conn.send(f"<Login>|False|Usuário ou senha inválidos.".encode())
						
					elif message.startswith("<File>"):
						# Envio de arquivo
						#broadcast(message, conn)
						file_info = message.split("|")
						file_name = file_info[1]
						file_size = int(file_info[2])
						
						print(f"<{thisUser}> sent a file: {file_name}")

						progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
						with open(file_name, "wb") as f:
							while True:
								# read bytes from the socket (receive)
								bytes_read = conn.recv(BUFFER_SIZE)
								if not bytes_read:    
									# nothing is received
									# file transmitting is done
									print('received')
									break
								# write to the file the bytes we just received
								f.write(bytes_read)
								# update the progress bar
								progress.update(len(bytes_read))
								
						broadcast(f"<{thisUser}> sent a file: {file_name}", conn)
					elif message.startswith("<Kick>"):
						info = message.split("|")
						user = info[1]
						kickUser = info[2]
						userIsMod = False
						if user in users:
							userIsMod = users[user]['mod']

						if userIsMod == True:
							if kickUser in loggedUsers:
								kickMessage = '/** ' + user + ' kickou ' + kickUser + ' **/'
								print(kickMessage)
								broadcast(kickMessage, conn)
								loggedUsers.remove(kickUser)
								for clients in list_of_clients:
									if clients==loggedUsers[kickUser]:
										clients.send(f"<Kicked>|Você foi kickado por " + user + ".".encode())
										remove(clients)
								conn.send(f"<Kick>|Usuário kickado com sucesso.".encode())
							else:
								conn.send(f"<Kick>|Usuário não existe.".encode())
						else:
							conn.send(f"<Kick>|Você não tem permissão para executar esta ação.".encode())
					elif message.startswith("<Emote>"):
						info = message.split("|")
						emote = info[1]
						if emote == "bear":
							emoteMessage = "ʕ·͡ᴥ·ʔ"
						elif emote == "angry":
							emoteMessage = "•`_´•"
						else:
							emoteMessage = "( ͡° ᴥ ͡°)﻿"
						
						message_to_send = "<" + thisUser + "> " + emoteMessage
						broadcast(message_to_send, {})
					elif message.startswith("<Logout>"):
						message_to_send = thisUser + " saiu."
						print("<" + thisUser + "> saiu.")
						broadcast(message_to_send, conn)
						remove(conn)
					else:
						message_to_send = "<" + thisUser + "> " + message
						broadcast(message_to_send, conn)
				else:
					print (addr[0] + " desconectou")

					remove(conn)

			except:
				continue
			

def broadcast(message, connection):
	for clients in list_of_clients:
		if clients!=connection:
			try:
				clients.send(message.encode())
			except:
				# if the link is broken, remove the client
				remove(clients)

def remove(connection):
	connection.close()

	if connection in list_of_clients:
		list_of_clients.remove(connection)

while True:
	conn, addr = server.accept()
	list_of_clients.append(conn)

	print (addr[0] + " conectou")

	# creates and individual thread for every user
	# that connects
	start_new_thread(clientthread,(conn,addr))	

conn.close()
server.close()

# Python program to implement client side of chat room.
import socket
import select
import sys
import os
import tqdm

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverName = '127.0.0.1'
serverPort = 5000
loggedIn = False
username = ''

server.connect((serverName,serverPort))

# Realiza o login
while not loggedIn:
	sockets_list = [sys.stdin, server]
	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

	for socks in read_sockets:
		if socks == server:
			message = socks.recv(BUFFER_SIZE).decode()
			if message.startswith("<Login>"):
				file_info = message.split("|")
				success = file_info[1]
				text = file_info[2]

				if success == 'True':
					print(text)
					username = nickname
					loggedIn = True
				else:
					print(text)
					nickname = input("Login: ")
					password = input("Senha: ")

					server.send(f"<Login>|{nickname}|{password}".encode())
			else:
				print(message)
				nickname = input("Login: ")
				password = input("Senha: ")

				server.send(f"<Login>|{nickname}|{password}".encode())

while True and loggedIn:
	# maintains a list of possible input streams
	sockets_list = [sys.stdin, server]

	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])

	for socks in read_sockets:
		if socks == server:
			message = socks.recv(BUFFER_SIZE).decode()

			# Recebendo Arquivo
			if message.startswith("<File>"):
				file_info = message.split("|")
				file_name = file_info[1]
				file_size = int(file_info[2])
				
				with open(file_name, "wb") as f:
					bytes_received = 0
					progress = tqdm.tqdm(range(file_size), f"Receiving {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
					while bytes_received < file_size:
						bytes_read = socks.recv(BUFFER_SIZE)
						f.write(bytes_read)
						bytes_received += len(bytes_read)
						progress.update(len(bytes_read))
				print(f"File '{file_name}' received.")
			elif message.startswith("<Kick>"):
				# Kick
				info = message.split("|")
				message = info[1]
				
				print(message)
			elif message.startswith("<Kicked>"):
				# Kick
				info = message.split("|")
				message = info[1]
				
				print(message)
				loggedIn = False
			else:
				# Recebendo Mensagem
				print(message)
		else:
			user_input = sys.stdin.readline().strip()
			if user_input == "/kick":
				kickUser = input("Digite o nome do usuário: ")
				server.send(f"<Kick>|{username}|{kickUser}".encode())
			elif user_input == "/sendfile":
				# Envia arquivo para o servidor
				file_path = input("Digite o caminho até: ")
				if os.path.exists(file_path) and os.path.isfile(file_path):
					file_name = os.path.basename(file_path)
					file_size = os.path.getsize(file_path)
					
					server.send(f"<File>|{file_name}|{file_size}".encode())
					
					progress = tqdm.tqdm(range(file_size), f"Sending {file_name}", unit="B", unit_scale=True, unit_divisor=1024)
					with open(file_name, "rb") as f:
						while True:
							# read the bytes from the file
							bytes_read = f.read(BUFFER_SIZE)

							if not bytes_read:
								# file transmitting is done
								break
							
							server.sendall(bytes_read)
							# update the progress bar
							progress.update(len(bytes_read))
						
					print(f"File '{file_name}' sent.")
				else:
					print("Invalid file path.")
			elif user_input == "/emote":
				emote = input("Emote: ")
				server.send(f"<Emote>|{emote}".encode())
			elif user_input == "/logout":
				server.send(f"<Logout>".encode())
				loggedIn = False
			else:
				# Envia mensagem para o servidor
				server.send(user_input.encode())
				sys.stdout.write(f"<{nickname}> {user_input}\n")
				sys.stdout.flush()

server.close()

import socket	#for sockets
import sys	#for exit
import select

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def ip_checksum(msg):
    s = 0
    for i in range(0, len(msg) - 1, 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
    ret = str(~s & 0xffff)
    while len(ret) < 5:
        ret = "0" + ret
    return ret


def rdt_send(data, ack, sock, addr):
	checksum = ip_checksum(data)
	to_send = str(checksum) + str(ack) + data
	sock.sendto(to_send.encode(), addr)


try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
	print("Failed to create socket")
	sys.exit()


def allTrue(a):
	for i in a:
		if a[i] == False:
			return False
	return True


host = 'localhost';
port = 8888;
window = 4

inputs = [s]
outputs = []

timeout = 10
ack_rcvd = [True, True, True, True]
msgs = ["one", "two", "three", "four"]


while(1) :
	if allTrue(ack_rcvd):
		print("Enter " + str(window) + " messages ")
		for i in range(0, window):
			msgs[i] = input(": ")
		print("Sending your data")
		for i in range(0, window):
			rdt_send(msgs[i], i, inputs[0], (host, port))
	
	readable, writable, exceptional = select.select( inputs, outputs, inputs, timeout)
	
	for tempSock in readable:
		count = [False, False, False, False]
		for i in range(0, window):
			try:
				d = tempSock.recvfrom(1024)
				reply = d[0].decode()
				addr = d[1]
			
				checksum = reply[:5]
				ack = reply[5]
				message = reply[6:]

				current = int(ack)
				if current > window:
					break

				calcSum = ip_checksum(message)
				if int(calcSum) == int(checksum):
					ack_rcvd[current] = True
					count[current] = True
				else:
					ack_rcvd[current] = False

			except socket.error as msg:
				print("Error Code: " + str(msg[0]) + "Message " + msg[1].decode())
				sys.exit()				

	if not allTrue(count):
		try: 
			print("Ack not recieved. Resending..")
			iput = input("enter")
			for i in range(0, window):
				rdt_send(msgs[i], i, inputs[0], (host, port))
				ack_rcvd[i] = False
		
	
		except socket.error as msg:
				print ("Error Code : " + str(msg[0]) + " Message " + msg[1].decode())
				sys.exit()
	else:
		print("all ACK's recieved to move on!")

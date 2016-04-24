# aserver1.py
# yield

import socket
from select import select
from collections import deque
from fib import fib

tasks = deque()
recv_wait = {}
send_wait = {}

def run():
  global tasks
  while any((tasks, recv_wait, send_wait)):

    while not tasks: # No active tasks, wait for I/O
      can_recv, can_send, [] = select(recv_wait, send_wait, [])
      for s in can_recv:
        tasks.append(recv_wait.pop(s))
      for s in can_send:
        tasks.append(send_wait.pop(s))

    task = tasks.popleft()
    try:
      why, what = next(task)  # run to the next yield statement
      if why == 'recv':
        # must go wait
        recv_wait[what] = task
      elif why == 'send':
        send_wait[what] = task
      else:
        raise ValueError('don\'t know task {0}'.format(why))
    except StopIteration:
      print("task done")

def fib_server(addr):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  sock.bind(addr)
  sock.listen(5)
  while True:
    yield 'recv', sock
    client, addr = sock.accept()                            # BLOCKING
    print('New connection from {0}'.format(addr))
    task = fib_handler(client, addr)
    tasks.append(task)
    

def fib_handler(client, addr):
  while True:
    yield 'recv', client
    req = client.recv(100)                                  # BLOCKING
    if not req:
      break
    n = int(req)
    result = fib(n)
    resp = str(result).encode('ascii') + b'\n'
    yield 'send', client
    client.send(resp)                                       # BLOCKING
  print("Closed connection to {0}".format(addr))

task = fib_server(('', 25000))
tasks.append(task)
run()

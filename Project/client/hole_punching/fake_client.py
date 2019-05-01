# Project/server/hole_punching/rendez_vous.py

"""
    UDP client.
    Only here for development purpose.

        1) Run server.py script (UDP server)
        2) Run this script (UDP client)
        4) You should see server response message
        5) Wait for server to close
"""

import socket


if __name__ == '__main__':
    message = 'Hello server !'.encode()
    # server_address = ('109.9.79.198', 5000)
    # server_address = ('localhost', 5000)
    server_address = ('109.9.79.198', 5000)

    # Create a UDP socket wrapped in safe environment
    # Auto handle close event if program crash
    # Sugar syntax similar to
    # try:
    #   Create and use socket
    # except Exception as e:
    #     raise e
    # finally:
    #     close socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Force a specific port for client
        sock.bind(('', 5000))
        # Define maximum time to wait between in each blocking call
        # sock.settimeout(1)

        # Send a fake message to test server response
        sent = sock.sendto(message, server_address)

        # # Check response
        # msg, addr = sock.recvfrom(4096)
        # print(msg.decode())
        # msg, addr = sock.recvfrom(4096)
        # print(msg.decode())

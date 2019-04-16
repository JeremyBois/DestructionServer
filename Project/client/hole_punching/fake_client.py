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
    server_address = ('localhost', 5000)

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
        # Send a fake message to test server response
        sent = sock.sendto(message, server_address)
        # Check response
        msg, addr = sock.recvfrom(4096)
        print(msg)

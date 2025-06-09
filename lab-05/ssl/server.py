import socket
import ssl
import threading
import os # To check for certificate files
import sys # For better error handling/logging

# --- Configuration ---
# Server address and port
SERVER_ADDRESS = ('localhost', 12345)
# Paths to SSL certificates (ensure these files exist in a 'certificates' directory)
CERT_FILE = "./certificates/server-cert.crt"
KEY_FILE = "./certificates/server-key.key"

# List to keep track of all connected client sockets
# This allows the server to broadcast messages to all clients.
clients = []
# A lock to protect the 'clients' list during modifications (adding/removing clients)
# This prevents race conditions when multiple threads try to modify the list simultaneously.
clients_lock = threading.Lock()

# --- Helper Function for Client Management ---
def remove_client(client_socket):
    """Safely removes a client socket from the global clients list."""
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
            print(f"Removed client: {client_socket.getpeerpeername()}")

# --- Client Handling Logic ---
def handle_client(client_socket):
    """
    Handles communication with a single connected client.
    This function runs in a separate thread for each client.
    """
    # Get the client's address for logging purposes
    client_address = client_socket.getpeername()
    print(f"Client connected: {client_address}")

    # Add the new client to the global list, protected by a lock
    with clients_lock:
        clients.append(client_socket)

    try:
        # Loop indefinitely to receive data from the client
        while True:
            # Receive up to 1024 bytes of data from the client
            data = client_socket.recv(1024)
            if not data:
                # If no data is received, the client has disconnected
                print(f"Client disconnected gracefully: {client_address}")
                break

            decoded_data = data.decode('utf-8').strip() # Decode and remove leading/trailing whitespace
            print(f"Received from {client_address}: {decoded_data}")

            # Prepare the message to broadcast (e.g., "client_address: message")
            broadcast_message = f"[{client_address[0]}:{client_address[1]}] {decoded_data}".encode('utf-8')

            # Iterate through all connected clients to broadcast the message
            # The lock is acquired here to ensure the 'clients' list doesn't change
            # while we're iterating over it.
            with clients_lock:
                for client in list(clients): # Use list() to iterate over a copy, safe if list changes
                    if client != client_socket: # Don't send the message back to the sender
                        try:
                            client.sendall(broadcast_message) # Use sendall for reliability
                        except ConnectionError:
                            # If sending fails, this client is likely disconnected
                            print(f"Failed to send to {client.getpeername()}, removing.")
                            remove_client(client)
                        except Exception as e:
                            print(f"An unexpected error occurred while sending to {client.getpeername()}: {e}")
                            remove_client(client)
    except ConnectionError as e:
        # Catches network-related errors (e.g., client forcefully disconnected)
        print(f"Connection error with {client_address}: {e}")
    except ssl.SSLError as e:
        # Catches SSL-specific errors
        print(f"SSL error with {client_address}: {e}")
    except Exception as e:
        # Catches any other unexpected errors during client handling
        print(f"An unexpected error occurred with {client_address}: {e}")
    finally:
        # Ensure the client socket is closed and removed from the list
        # This block always executes, whether the loop breaks or an exception occurs.
        print(f"Closing connection for {client_address}")
        remove_client(client_socket) # Safe removal
        client_socket.close() # Close the socket

# --- Server Setup and Main Loop ---
def start_server():
    """Initializes and starts the secure chat server."""
    # Check if certificate files exist before starting
    if not os.path.exists(CERT_FILE):
        print(f"Error: Certificate file not found at {CERT_FILE}")
        sys.exit(1)
    if not os.path.exists(KEY_FILE):
        print(f"Error: Key file not found at {KEY_FILE}")
        sys.exit(1)

    # 1. Create a standard TCP/IP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allows reuse of the address quickly after the server is stopped
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # 2. Bind the socket to the specified address and port
        server_socket.bind(SERVER_ADDRESS)
        # 3. Enable the server to accept connections
        server_socket.listen(5) # Allow up to 5 pending connections
        print(f"Server listening on {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}...")

        # 4. Create an SSL context
        # PROTOCOL_TLS ensures the most secure TLS version available is used
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # Load the server's certificate and private key
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        # Optionally, configure client certificate verification (if needed for mutual TLS)
        # context.verify_mode = ssl.CERT_REQUIRED
        # context.load_verify_locations(cafile="./certificates/ca-cert.crt")

        # Main loop to accept new client connections
        while True:
            # Accept a new incoming connection
            client_socket, client_address = server_socket.accept()
            # Wrap the standard socket with SSL/TLS encryption
            ssl_socket = context.wrap_socket(client_socket, server_side=True)

            # Start a new thread to handle the communication with this specific client
            client_thread = threading.Thread(target=handle_client, args=(ssl_socket,))
            client_thread.daemon = True # Allow main program to exit even if threads are running
            client_thread.start()

    except OSError as e:
        # Catches errors like "Address already in use" if the port is busy
        print(f"Operating system error: {e}")
        print("Please ensure the port is not already in use or try again after a moment.")
    except ssl.SSLError as e:
        # Catches errors related to SSL certificate loading or handshakes
        print(f"SSL configuration error: {e}")
        print("Please check your certificate paths and file permissions.")
    except Exception as e:
        # Catches any other unexpected errors during server startup or main loop
        print(f"An unhandled error occurred: {e}")
    finally:
        # Ensure the server socket is closed when the program exits
        print("Shutting down server socket.")
        server_socket.close()

# --- Entry Point ---
if __name__ == "__main__":
    # This ensures start_server() is called only when the script is executed directly
    start_server()

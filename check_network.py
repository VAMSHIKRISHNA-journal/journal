import socket

def check_connection(host, port):
    try:
        print(f"Attempting to connect to {host}:{port}...")
        socket.create_connection((host, port), timeout=10)
        print(f"Successfully connected to {host}:{port}")
        return True
    except Exception as e:
        print(f"Connection to {host}:{port} failed: {e}")
        return False

if __name__ == "__main__":
    check_connection("smtp.gmail.com", 587)
    check_connection("smtp.gmail.com", 465)
    check_connection("8.8.8.8", 53) # Internet check

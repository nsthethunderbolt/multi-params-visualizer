import qrcode
import socket
import time

# Get local IP
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
def showqr():
    ip = get_ip()
    port = 8050
    url = f"http://{ip}:{port}"

    # Generate QR code
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make()
    qr.print_ascii()  # You can scan directly from terminal 🎯


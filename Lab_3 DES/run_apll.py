import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import os
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad

# ================= CONFIG =================
HOST = '0.0.0.0'
PORT = 6000
HEADER_SIZE = 16

client_socket = None

# ================= DES =================
def encrypt_des_cbc(plaintext):
    key = os.urandom(8)   # DES key 8 bytes
    iv = os.urandom(8)

    cipher = DES.new(key, DES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, 8))

    return key, iv, ciphertext

def decrypt_des_cbc(key, iv, ciphertext):
    cipher = DES.new(key, DES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), 8)
    return plaintext

# ================= PACKET =================
def build_packet(key, iv, cipher):
    length = len(cipher)
    header = key + iv + length.to_bytes(4, 'big')
    return header + cipher

def parse_header(header):
    key = header[:8]
    iv = header[8:16]
    length = int.from_bytes(header[16:20], 'big')
    return key, iv, length

def recv_exact(conn, size):
    data = b''
    while len(data) < size:
        packet = conn.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data

# ================= GUI =================
root = tk.Tk()
root.title("🔐 Secure DES Chat")
root.geometry("650x550")
root.configure(bg="#0f172a")

BG = "#0f172a"
CHAT_BG = "#020617"
FG = "#e2e8f0"
ACCENT = "#38bdf8"

title = tk.Label(root, text="SECURE CHAT", font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=ACCENT)
title.pack(pady=10)

chat_box = scrolledtext.ScrolledText(
    root, bg=CHAT_BG, fg=FG,
    font=("Consolas", 10),
    insertbackground="white", bd=0
)
chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def log(msg, sender="SYS"):
    time = datetime.now().strftime("%H:%M:%S")
    chat_box.insert(tk.END, f"[{time}] {sender}: {msg}\n")
    chat_box.see(tk.END)

frame = tk.Frame(root, bg=BG)
frame.pack(pady=5)

entry = tk.Entry(frame, width=40, bg="#1e293b", fg="white",
                 insertbackground="white", bd=0, font=("Segoe UI", 11))
entry.grid(row=0, column=0, padx=5, ipady=6)

# ================= SERVER =================
def handle_client(conn):
    global client_socket
    client_socket = conn

    while True:
        try:
            header = recv_exact(conn, 20)
            if not header:
                log("Disconnected")
                break

            key, iv, length = parse_header(header)
            cipher_bytes = recv_exact(conn, length)

            plaintext = decrypt_des_cbc(key, iv, cipher_bytes)

            try:
                msg = plaintext.decode("utf-8")
            except:
                msg = str(plaintext)

            log(msg, "PEER")

        except Exception as e:
            log(f"Receive error: {e}")
            break

def start_server():
    def server_thread():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            log(f"Listening on {PORT}")

            conn, addr = s.accept()
            log(f"Connected from {addr}")

            threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

    threading.Thread(target=server_thread, daemon=True).start()

# ================= CLIENT =================
def connect_to_server():
    global client_socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = entry.get().strip()

        s.connect((ip, PORT))
        client_socket = s

        log(f"Connected to {ip}")
        threading.Thread(target=handle_client, args=(s,), daemon=True).start()

    except Exception as e:
        log(f"Connect error: {e}")

# ================= SEND =================
def send_message():
    global client_socket

    if not client_socket:
        log("Not connected!")
        return

    msg = entry.get().strip()
    if not msg:
        return

    try:
        plain = msg.encode("utf-8")

        key, iv, cipher = encrypt_des_cbc(plain)
        packet = build_packet(key, iv, cipher)

        client_socket.sendall(packet)

        log(msg, "ME")
        entry.delete(0, tk.END)

    except Exception as e:
        log(f"Send error: {e}")

# ================= BUTTON =================
def btn(text, cmd):
    return tk.Button(frame, text=text, command=cmd,
                     bg=ACCENT, fg="black",
                     font=("Segoe UI", 10, "bold"),
                     bd=0, padx=10)

btn("Start Server", start_server).grid(row=0, column=1, padx=5)
btn("Connect", connect_to_server).grid(row=0, column=2, padx=5)
btn("Send", send_message).grid(row=0, column=3, padx=5)

entry.bind("<Return>", lambda e: send_message())

root.mainloop()
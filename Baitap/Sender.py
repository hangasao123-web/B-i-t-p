import socket
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import threading
import time

SERVER_IP = '26.182.218.70'
DATA_PORT = 5000
KEY_PORT = 5001

# ===== Phong cách gui hacker =====
root = tk.Tk()
root.title("Trình gửi AES")
root.geometry("700x500")
root.configure(bg="black")

# ===== Ô NHẬP TIN NHẮN =====
msg_entry = tk.Entry(root, width=80, bg="black", fg="#00ff00",
                     insertbackground="#00ff00", font=("Consolas", 12))
msg_entry.pack(pady=5)
msg_entry.focus()

# ===== KHUNG LOG =====
log_box = ScrolledText(root, bg="black", fg="#00ff00", font=("Consolas", 11))
log_box.pack(fill="both", expand=True, padx=10, pady=10)

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update()

# ===== Chức năng chính =====
def start_sender():
    try:
        message = msg_entry.get()

        if message.strip() == "":
            log("[!] Vui lòng nhập tin nhắn!")
            return

        log("[+] Khởi tạo module mã hóa AES...")
        time.sleep(0.5)

        # Tạo key + IV
        aes_key = get_random_bytes(16)
        iv = get_random_bytes(16)

        data_to_encrypt = message.encode()

        # ===== Gửi KEY =====
        log("[*] Đang kết nối server KEY...")
        key_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        key_s.connect((SERVER_IP, KEY_PORT))
        log("[+] Kết nối KEY thành công")

        key_s.send(aes_key)
        key_s.send(iv)
        key_s.close()

        log("[+] Đã gửi KEY + IV thành công!")
        time.sleep(0.5)

        # ===== MÃ HÓA =====
        log("[*] Đang mã hóa dữ liệu AES CBC...")
        cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
        ciphertext = cipher.encrypt(pad(data_to_encrypt, AES.block_size))
        log("[+] Mã hóa hoàn tất")

        # ===== Gửi DATA =====
        log("[*] Đang kết nối server DATA...")
        data_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_s.connect((SERVER_IP, DATA_PORT))
        log("[+] Kết nối DATA thành công")

        header = len(ciphertext).to_bytes(4, byteorder='big')
        data_s.send(header)
        data_s.send(ciphertext)
        data_s.close()

        log("[+] Đã gửi dữ liệu mã hóa thành công!")
        log("\n>>> HOÀN THÀNH <<<")

        # Xóa ô nhập sau khi gửi
        msg_entry.delete(0, tk.END)

    except Exception as e:
        log("[!] LỖI: " + str(e))


def run_thread():
    threading.Thread(target=start_sender).start()

# ===== ENTER ĐỂ GỬI =====
def send_by_enter(event):
    run_thread()

msg_entry.bind("<Return>", send_by_enter)

# ===== BUTTON =====
btn = tk.Button(root, text="GỬI TIN NHẮN", command=run_thread,
                bg="black", fg="#00ff00", font=("Consolas", 14))
btn.pack(pady=10)

root.mainloop()
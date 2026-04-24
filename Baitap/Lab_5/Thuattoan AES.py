from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii
import sys


def parse_key(key_input: str) -> bytes:
    key_input = key_input.strip()
    if len(key_input) == 16:
        return key_input.encode('utf-8')

    if len(key_input) == 32:
        try:
            return binascii.unhexlify(key_input)
        except (binascii.Error, ValueError):
            pass

    raise ValueError('Key phai la 16 ky tu ASCII hoac 32 ky tu HEX.')


def to_hex(data: bytes) -> str:
    return binascii.hexlify(data).decode('utf-8')


def from_hex(data: str) -> bytes:
    try:
        return binascii.unhexlify(data.strip())
    except (binascii.Error, ValueError):
        raise ValueError('Du lieu hex khong hop le.')


def encrypt_text(plain_text: str, key: bytes) -> str:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))
    return to_hex(iv + ciphertext)


def decrypt_text(cipher_hex: str, key: bytes) -> str:
    data = from_hex(cipher_hex)
    if len(data) < 32 or len(data) % 16 != 0:
        raise ValueError('Du lieu ma hoa phai co dinh dang IV+ciphertext voi do dai boi so 16.')

    iv = data[:16]
    ciphertext = data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plain.decode('utf-8')


def show_menu() -> None:
    print('=== Thuat toan AES-128 (Python) ===')
    print('1. Ma hoa (encrypt)')
    print('2. Giai ma (decrypt)')
    print('0. Thoat')


def main() -> None:
    while True:
        show_menu()
        choice = input('Lua chon: ').strip()
        if choice == '0':
            print('Thoat.')
            break

        if choice not in {'1', '2'}:
            print('Lua chon khong hop le. Vui long chon lai.\n')
            continue

        key_input = input('Nhap key AES-128 (16 ky tu ASCII hoac 32 ky tu HEX): ')
        try:
            key = parse_key(key_input)
        except ValueError as err:
            print(f'Key khong hop le: {err}\n')
            continue

        if choice == '1':
            plain_text = input('Nhap van ban can ma hoa: ')
            cipher_hex = encrypt_text(plain_text, key)
            print(f'Ket qua ma hoa (HEX): {cipher_hex}\n')
        else:
            cipher_hex = input('Nhap ban ma hex can giai ma (IV + ciphertext): ')
            try:
                plain_text = decrypt_text(cipher_hex, key)
                print(f'Van ban goc: {plain_text}\n')
            except ValueError as err:
                print(f'Giai ma that bai: {err}\n')
            except UnicodeDecodeError:
                print('Giai ma thanh cong nhung khong the chuyen sang chuoi UTF-8.\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nThoat boi nguoi dung.')
        sys.exit(0)

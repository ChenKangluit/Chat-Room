import socket
import ssl
import threading

from cryptography.fernet import Fernet

SERVER = '127.0.0.1'
PORT = 5555


def receive(client_socket, cipher_suite):
    try:
        while True:
            encrypted_message = client_socket.recv(1024)
            print(f"密文:{encrypted_message}")
            if not encrypted_message:
                break
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            print(decrypted_message)

    except Exception as e:
        print(f"接收或解密消息出错: {e}")


def send(client_socket, cipher_suite):
    try:
        while True:
            message = input()
            encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
            client_socket.send(encrypted_message)
            if message.lower() == 'quit':
                break

    except Exception as e:
        print(f"发送或加密消息出错: {e}")


def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("..\\path\\to\\ca_cert.pem")
        context.check_hostname = False  # 关闭主机名验证
        context.verify_mode = ssl.CERT_NONE  # 禁用服务器证书验证

        secure_socket = context.wrap_socket(client, server_hostname=SERVER)
        print("Connecting to the server...")
        secure_socket.connect((SERVER, PORT))
        print("Connected to the server")

        key = secure_socket.recv(1024)
        cipher_suite = Fernet(key)
        print(f"收到密钥: {key}")

        nickname = input("输入您的昵称: ")
        encrypted_nickname = cipher_suite.encrypt(nickname.encode('utf-8'))
        secure_socket.send(encrypted_nickname)

        encrypted_welcome_message = secure_socket.recv(1024)
        welcome_message = cipher_suite.decrypt(encrypted_welcome_message).decode('utf-8')
        print(welcome_message)

        receive_thread = threading.Thread(target=receive, args=(secure_socket, cipher_suite))
        receive_thread.start()

        send_thread = threading.Thread(target=send, args=(secure_socket, cipher_suite))
        send_thread.start()

        send_thread.join()
        receive_thread.join()

    except Exception as e:
        print(f"连接服务器出错: {e}")


if __name__ == "__main__":
    main()

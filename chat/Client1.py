import socket
import threading

from cryptography.fernet import Fernet

# 服务器配置
SERVER = '127.0.0.1'
PORT = 5555


def receive(client_socket, cipher_suite):
    try:
        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            # 密文
            print(encrypted_message)
            # print(f"收到消息: {decrypted_message}")
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
        client.connect((SERVER, PORT))

        # 接收服务器发送的加密密钥
        key = client.recv(1024)
        cipher_suite = Fernet(key)

        # 发送昵称
        nickname = input("输入您的昵称: ")
        encrypted_nickname = cipher_suite.encrypt(nickname.encode('utf-8'))
        client.send(encrypted_nickname)

        # 接收并显示欢迎消息
        encrypted_welcome_message = client.recv(1024)
        welcome_message = cipher_suite.decrypt(encrypted_welcome_message).decode('utf-8')
        print(welcome_message)

        # 启动发送和接收消息的线程
        receive_thread = threading.Thread(target=receive, args=(client, cipher_suite))
        receive_thread.start()

        send_thread = threading.Thread(target=send, args=(client, cipher_suite))
        send_thread.start()

        send_thread.join()
        receive_thread.join()

    except Exception as e:
        print(f"连接服务器出错: {e}")


if __name__ == "__main__":
    main()

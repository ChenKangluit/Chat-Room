import socket
import threading

import rsa
from cryptography.fernet import Fernet

import keys  # 导入keys模块，假设此模块包含用于加载密钥的函数

# 加载私钥
private_key = keys.load_private_key()  # 从 keys 模块中加载 RSA 私钥


def start_client():
    # 创建一个 TCP/IP 套接字
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # 连接到服务器
        client.connect(("127.0.0.1", 5555))

        # 接收服务器发送的加密对称秘钥
        encrypted_symmetric_key = client.recv(256)  # 接收256字节的加密对称密钥
        print(f"接收到的加密对称秘钥: {encrypted_symmetric_key}")

        try:
            # 使用 RSA 私钥解密对称密钥
            symmetric_key = rsa.decrypt(encrypted_symmetric_key, private_key)
            print(f"解密后的对称秘钥: {symmetric_key}")
        except rsa.DecryptionError as e:
            # 如果解密失败，输出错误并返回
            print(f"解密失败: {e}")
            return

        # 创建一个 Fernet 密码套件对象，用于加密和解密消息
        cipher_suite = Fernet(symmetric_key)

        def receive_messages():
            while True:
                try:
                    # 接收服务器发送的消息
                    message = client.recv(1024)
                    if not message:
                        break
                    print(f"密文:{message}")
                    # 解密接收到的消息
                    decrypted_message = cipher_suite.decrypt(message)
                    print(f"收到消息: {decrypted_message.decode()}")
                except Exception as e:
                    # 如果接收消息时出错，输出错误并退出循环
                    print(f"接收消息时出错: {e}")
                    break

        # 启动接收消息的线程
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()

        while True:
            # 读取用户输入的消息
            message = input("")
            # 使用对称密钥加密消息
            encrypted_message = cipher_suite.encrypt(message.encode())
            # 发送加密后的消息到服务器
            client.send(encrypted_message)
    except ConnectionResetError as e:
        # 如果连接被服务器重置，输出错误
        print(f"连接被服务器重置: {e}")
    finally:
        # 关闭客户端套接字
        client.close()


if __name__ == "__main__":
    start_client()  # 启动客户端

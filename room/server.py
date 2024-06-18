import socket
import threading
import rsa
from cryptography.fernet import Fernet
import keys  # 导入keys模块

# 加载公钥
public_key = keys.load_public_key()

# 存储客户端信息和加密秘钥
clients = {}
client_keys = {}
nick_name = {}

def handle_client(client_socket, address):
    """
    处理客户端连接的函数，负责接收加密的对称秘钥，解密消息并转发给其他客户端。
    :param client_socket: 客户端套接字
    :param address: 客户端地址
    """
    try:
        # 生成对称加密秘钥
        symmetric_key = Fernet.generate_key()
        cipher_suite = Fernet(symmetric_key)

        # 使用RSA公钥加密对称加密秘钥
        encrypted_symmetric_key = rsa.encrypt(symmetric_key, public_key)
        print(f"发送给客户端的加密对称秘钥: {encrypted_symmetric_key}")
        client_socket.send(encrypted_symmetric_key)

        # 存储客户端和其加密秘钥
        clients[client_socket] = address
        client_keys[client_socket] = cipher_suite

        while True:
            try:
                # 接收消息
                message = client_socket.recv(1024)
                if not message:
                    break
                # 解密消息
                decrypted_message = cipher_suite.decrypt(message)
                print(f"[{address}] 明文: {decrypted_message.decode()}")

                # 转发消息给其他客户端
                for client in clients:
                    if client != client_socket:
                        encrypted_message = client_keys[client].encrypt(decrypted_message)
                        client.send(encrypted_message)
            except Exception as e:
                print(f"处理消息时出错: {e}")
                break
    except Exception as e:
        print(f"处理客户端时出错: {e}")
    finally:
        client_socket.close()
        if client_socket in clients:
            del clients[client_socket]
        if client_socket in client_keys:
            del client_keys[client_socket]


def start_server():
    """
    启动服务器，监听客户端连接并为每个连接创建一个新线程处理。
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    print("[*] 服务器启动，等待连接...")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] 接收到连接: {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()


if __name__ == "__main__":
    start_server()

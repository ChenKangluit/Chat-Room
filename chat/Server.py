import socket
import threading

from cryptography.fernet import Fernet

# 全局变量
clients = {}
addresses = {}
clients_lock = threading.Lock()

# 服务器配置
HOST = '127.0.0.1'
PORT = 5555


def generate_key():
    # 生成一个随机的加密密钥
    return Fernet.generate_key()


def handle_client(client_socket, addr):
    try:
        # 生成并发送加密密钥
        key = generate_key()
        cipher_suite = Fernet(key)
        client_socket.send(key)
        # print(f"密钥:{key}")

        # 接收并解密昵称
        encrypted_nickname = client_socket.recv(1024)
        nickname = cipher_suite.decrypt(encrypted_nickname).decode('utf-8')
        welcome_message = f"欢迎 {nickname} 进入聊天室！输入 'quit' 退出。当前在线人数: {len(clients) + 1}/10"
        client_socket.send(cipher_suite.encrypt(welcome_message.encode('utf-8')))

        # 将客户端添加到字典
        with clients_lock:
            clients[client_socket] = (nickname, cipher_suite)
            addresses[client_socket] = addr

        # 广播新用户加入聊天室并更新在线人数
        broadcast(f"{nickname} 加入了聊天室!")
        update_online_count()

        while True:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break

            decrypted_message = cipher_suite.decrypt(encrypted_message).decode('utf-8')
            if decrypted_message.lower() == 'quit':
                client_socket.close()
                with clients_lock:
                    del clients[client_socket]
                broadcast(f"{nickname} 离开了聊天室。")
                update_online_count()
                break
            else:
                broadcast(f"{nickname}: {decrypted_message}", client_socket)

    except Exception as e:
        print(f"处理客户端 {addr} 出错: {e}")


def broadcast(message, sender_socket=None):
    with clients_lock:
        for client_socket, (nickname, cipher_suite) in clients.items():
            if client_socket != sender_socket:  # 确保不向消息发送者自己发送消息
                try:
                    encrypted_message = cipher_suite.encrypt(message.encode('utf-8'))
                    client_socket.send(encrypted_message)
                except Exception as e:
                    print(f"无法发送消息给 {nickname}: {e}")


def update_online_count():
    with clients_lock:
        count_message = f"当前在线人数: {len(clients)}"
        print(count_message)
        for client_socket, (nickname, cipher_suite) in clients.items():
            try:
                encrypted_message = cipher_suite.encrypt(count_message.encode('utf-8'))
                client_socket.send(encrypted_message)
            except Exception as e:
                print(f"无法发送在线人数消息给 {nickname}: {e}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"服务器启动在 {HOST}:{PORT}")

    while True:
        client_socket, client_addr = server.accept()
        print(f"新连接来自 {client_addr}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
        client_thread.start()


if __name__ == "__main__":
    main()

import socket
import ssl
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
    return Fernet.generate_key()


def handle_client(client_socket, addr):
    try:
        key = generate_key()
        print(f"密钥:{key}")
        cipher_suite = Fernet(key)
        client_socket.send(key)
        print(f"密钥已发送给 {addr}")

        encrypted_nickname = client_socket.recv(1024)
        nickname = cipher_suite.decrypt(encrypted_nickname).decode('utf-8')
        print(f"{addr} 的昵称是 {nickname}")
        welcome_message = f"欢迎 {nickname} 进入聊天室！输入 'quit' 退出。当前在线人数: {len(clients) + 1}/10"
        client_socket.send(cipher_suite.encrypt(welcome_message.encode('utf-8')))
        print(f"已发送欢迎消息给 {nickname}")

        # 使用线程锁 (clients_lock) 来确保多个线程在访问和修改这些共享资源时不会出现数据不一致的问题。
        with clients_lock:
            clients[client_socket] = (nickname, cipher_suite)
            addresses[client_socket] = addr

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
            if client_socket != sender_socket:
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
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(10)
        print(f"服务器启动在 {HOST}:{PORT}")

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile="D:/path/to/server_cert.pem", keyfile="D:/path/to/server_key.pem")
        context.load_verify_locations("D:/path/to/ca_cert.pem")
        print("SSL 上下文已加载")

        while True:
            print("等待新连接...")
            client_socket, client_addr = server.accept()
            print(f"新连接来自 {client_addr}")
            try:
                secure_socket = context.wrap_socket(client_socket, server_side=True)
                print(f"已建立 SSL 连接 {client_addr}")
                client_thread = threading.Thread(target=handle_client, args=(secure_socket, client_addr))
                client_thread.start()
            except ssl.SSLError as e:
                print(f"SSL 错误: {e}")
                client_socket.close()

    except Exception as e:
        print(f"服务器启动出错: {e}")


if __name__ == "__main__":
    main()



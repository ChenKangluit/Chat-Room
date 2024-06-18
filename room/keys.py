import os

import rsa

KEY_DIR = "./keys"
PUBLIC_KEY_FILE = os.path.join(KEY_DIR, "public_key.pem")
PRIVATE_KEY_FILE = os.path.join(KEY_DIR, "private_key.pem")


def ensure_key_dir():
    """
    确保密钥存储目录存在。如果目录不存在，则创建它。
    """
    if not os.path.exists(KEY_DIR):
        os.makedirs(KEY_DIR)


def generate_keys():
    """
    生成一对RSA密钥（公钥和私钥），并将它们分别保存到名为"public_key.pem"和"private_key.pem"的文件中。
    使用2048位的密钥长度以增加安全性。
    """
    public_key, private_key = rsa.newkeys(2048)  # 使用2048位密钥以增加安全性
    with open(PUBLIC_KEY_FILE, "wb") as p:
        p.write(public_key.save_pkcs1("PEM"))  # 将公钥保存为PEM格式的文件
    with open(PRIVATE_KEY_FILE, "wb") as p:
        p.write(private_key.save_pkcs1("PEM"))  # 将私钥保存为PEM格式的文件


def load_public_key():
    """
    从名为"public_key.pem"的文件中加载RSA公钥。
    :return: RSA公钥对象
    """
    with open(PUBLIC_KEY_FILE, "rb") as p:
        return rsa.PublicKey.load_pkcs1(p.read())  # 读取并加载公钥


def load_private_key():
    """
    从名为"private_key.pem"的文件中加载RSA私钥。
    :return: RSA私钥对象
    """
    with open(PRIVATE_KEY_FILE, "rb") as p:
        return rsa.PrivateKey.load_pkcs1(p.read())  # 读取并加载私钥


def get_or_create_keys():
    """
    检查密钥文件是否存在。如果存在，则加载它们；如果不存在，则生成新密钥。
    """
    ensure_key_dir()
    if not os.path.exists(PUBLIC_KEY_FILE) or not os.path.exists(PRIVATE_KEY_FILE):
        print("密钥文件不存在，正在生成新密钥...")
        generate_keys()
    else:
        print("密钥文件已存在，正在加载密钥...")


# 在客户端和服务器端初始化时调用
get_or_create_keys()

# 加载密钥
public_key = load_public_key()
private_key = load_private_key()

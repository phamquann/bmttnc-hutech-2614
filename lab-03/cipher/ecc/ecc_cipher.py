import ecdsa, os

if not os.path.exists('cipher/ecc/keys'):
    os.makedirs('cipher/ecc/keys')

class ECCCipher:
    def __init__(self):
        pass
    
    def generate_keys(self):
        sk = ecdsa.SigningKey.generate()    
        vk = sk.get_verifying_key()         
        
        with open('cipher/ecc/keys/privatekey.pem', 'wb') as p:
            p.write(sk.to_pem())
        
        with open('cipher/ecc/keys/publickey.pem', 'wb') as p:
            p.write(vk.to_pem())
    
    def load_keys(self):
        with open('cipher/ecc/keys/privatekey.pem', 'rb') as p:
            sk = ecdsa.SigningKey.from_pem(p.read())
        
        with open('cipher/ecc/keys/publickey.pem', 'rb') as p:
            vk = ecdsa.VerifyingKey.from_pem(p.read())
        
        return sk, vk
    
    def sign(self, message, key):
        return key.sign(message.encode('ascii'))
    
    def verify(self, message, signature, key):  # ✅ Thêm indent vào đây
        try:
            return key.verify(signature, message.encode('ascii'))  # ✅ Dùng key parameter
        except ecdsa.BadSignatureError:
            return False
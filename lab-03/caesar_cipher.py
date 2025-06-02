import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui.caesar import Ui_MainWindow
import requests

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Debug: In ra tất cả các widget có sẵn
        print("Available widgets:")
        widgets = [attr for attr in dir(self.ui) if not attr.startswith('_') and not callable(getattr(self.ui, attr))]
        for widget in widgets:
            print(f"  - {widget}")
        
        # Thử connect với các tên button có thể có
        self.connect_buttons()
        
    def connect_buttons(self):
        # Danh sách các tên button có thể có
        encrypt_button_names = ['btn_encrypt', 'pushButton', 'encryptButton', 'encrypt_btn', 'btnEncrypt']
        decrypt_button_names = ['btn_decrypt', 'pushButton_2', 'decryptButton', 'decrypt_btn', 'btnDecrypt']
        
        # Tìm và connect encrypt button
        encrypt_connected = False
        for name in encrypt_button_names:
            if hasattr(self.ui, name):
                getattr(self.ui, name).clicked.connect(self.call_api_encrypt)
                print(f"Connected encrypt button: {name}")
                encrypt_connected = True
                break
        
        if not encrypt_connected:
            print("Warning: Encrypt button not found!")
            
        # Tìm và connect decrypt button
        decrypt_connected = False
        for name in decrypt_button_names:
            if hasattr(self.ui, name):
                getattr(self.ui, name).clicked.connect(self.call_api_decrypt)
                print(f"Connected decrypt button: {name}")
                decrypt_connected = True
                break
                
        if not decrypt_connected:
            print("Warning: Decrypt button not found!")

    def get_text_widget_content(self, widget_names):
        """Lấy nội dung từ text widget với nhiều tên có thể có"""
        for name in widget_names:
            if hasattr(self.ui, name):
                widget = getattr(self.ui, name)
                if hasattr(widget, 'toPlainText'):
                    return widget.toPlainText()
                elif hasattr(widget, 'text'):
                    return widget.text()
        return ""
    
    def set_text_widget_content(self, widget_names, content):
        """Set nội dung cho text widget với nhiều tên có thể có"""
        for name in widget_names:
            if hasattr(self.ui, name):
                widget = getattr(self.ui, name)
                if hasattr(widget, 'setText'):
                    widget.setText(content)
                    return True
        return False

    def call_api_encrypt(self):
        url = "http://127.0.0.1:5000/api/caesar/encrypt"
        
        # Lấy plain text với nhiều tên có thể có
        plain_text_names = ['txt_plain_text', 'plainTextEdit', 'textEdit', 'lineEdit']
        plain_text = self.get_text_widget_content(plain_text_names)
        
        # Lấy key với nhiều tên có thể có (dựa vào widget list, key có thể là lineEdit)
        key_names = ['txt_key', 'keyLineEdit', 'lineEdit_2', 'keyEdit', 'lineEdit']
        key_text = self.get_text_widget_content(key_names)
        
        # Validate key
        if not key_text.strip():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please enter a key!")
            msg.exec_()
            return
            
        try:
            key = int(key_text.strip())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Key must be a number!")
            msg.exec_()
            return
        
        payload = {
            "plain_text": plain_text,
            "key": str(key)  # Convert to string for API
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {data}")  # Debug: xem API trả về gì
                
                # API trả về 'encrypted_text' không phải 'encrypted_message'
                encrypted_text = data.get("encrypted_text") or data.get("encrypted_message", "")
                
                # Set cipher text với nhiều tên có thể có
                cipher_text_names = ['txt_cipher_text', 'cipherTextEdit', 'textEdit_2', 'lineEdit_3']
                if not self.set_text_widget_content(cipher_text_names, encrypted_text):
                    print("Warning: Could not find cipher text widget to display result")
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Encrypted Successfully")
                msg.exec_()
            else:
                print(f"Error while calling API. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def call_api_decrypt(self):
        url = "http://127.0.0.1:5000/api/caesar/decrypt"
        
        # Lấy cipher text với nhiều tên có thể có
        cipher_text_names = ['txt_cipher_text', 'cipherTextEdit', 'textEdit_2', 'lineEdit_3']
        cipher_text = self.get_text_widget_content(cipher_text_names)
        
        # Lấy key với nhiều tên có thể có (dựa vào widget list, key có thể là lineEdit)
        key_names = ['txt_key', 'keyLineEdit', 'lineEdit_2', 'keyEdit', 'lineEdit']
        key_text = self.get_text_widget_content(key_names)
        
        # Validate key
        if not key_text.strip():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please enter a key!")
            msg.exec_()
            return
            
        try:
            key = int(key_text.strip())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Key must be a number!")
            msg.exec_()
            return
        
        payload = {
            "cipher_text": cipher_text,
            "key": str(key)  # Convert to string for API
        }
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                print(f"API Response: {data}")  # Debug: xem API trả về gì
                
                # API có thể trả về 'decrypted_text' hoặc 'decrypted_message'
                decrypted_text = data.get("decrypted_text") or data.get("decrypted_message", "")
                
                # Set plain text với nhiều tên có thể có
                plain_text_names = ['txt_plain_text', 'plainTextEdit', 'textEdit', 'lineEdit']
                if not self.set_text_widget_content(plain_text_names, decrypted_text):
                    print("Warning: Could not find plain text widget to display result")
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Decrypted Successfully")
                msg.exec_()
            else:
                print(f"Error while calling API. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
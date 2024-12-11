import os
import json
import hmac
import hashlib
from cryptography.fernet import Fernet


class SecureJSON:
    """
    A comprehensive class for secure JSON file handling with encryption and integrity checks.
    """

    def __init__(self, secret_key=None, key_path='encryption_key.key', signature_key_path='signature_key.key'):
        """
        Initialize SecureJSON with consistent key management.
        This function takes
            secret_key: Custom secret key for signing.
            key_path: Path to store/load encryption key.
            signature_key_path: Path to store/load signature key.
        """
        self.key_path = key_path
        self.signature_key_path = signature_key_path
        self._setup_encryption_key()
        self._setup_signature_key(secret_key)

    def _setup_encryption_key(self):
        """
        Generate or load encryption key.
        """
        try:
            with open(self.key_path, 'rb') as key_file:
                self.encryption_key = key_file.read()
        except FileNotFoundError:
            self.encryption_key = Fernet.generate_key()
            with open(self.key_path, 'wb') as key_file:
                key_file.write(self.encryption_key)
        self.cipher = Fernet(self.encryption_key)

    def _setup_signature_key(self, custom_key=None):
        """
        Generate or load signature key.
        """
        try:
            with open(self.signature_key_path, 'rb') as key_file:
                self.signature_key = key_file.read()
        except FileNotFoundError:
            if custom_key:
                self.signature_key = custom_key.encode(
                    'utf-8') if isinstance(custom_key, str) else custom_key
            else:
                self.signature_key = os.urandom(32)
            with open(self.signature_key_path, 'wb') as key_file:
                key_file.write(self.signature_key)

    def encrypt(self, data, output_path):
        """
        Encrypt data and save to a file with signature.
        This function takes
            data: Data to encrypt
            output_path: File path to save encrypted data
        """
        json_string = json.dumps(data, sort_keys=True)

        # Create signature
        signature = hmac.new(
            self.signature_key,
            json_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        encrypted_data = self.cipher.encrypt(json_string.encode('utf-8'))

        payload = {
            'data': encrypted_data.decode('latin1'),
            'signature': signature
        }

        with open(output_path, 'w',  encoding="utf-8") as file:
            json.dump(payload, file)
       # This is for you to see not encrypt data that the only use of the file   
        with open(f"not_encrypt_file_for_you_to_see_{output_path}", 'w',  encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def decrypt(self, file_path):
        """
        Decrypt and verify data from an encrypted file.
        This function takes
            file_path: Path to encrypted file
        Returns:
            dict: Decrypted data if signature is valid
            None: If decryption or verification fails
        """
        try:
            with open(file_path, 'r',  encoding="utf-8") as file:
                payload = json.load(file)

            encrypted_data = payload['data'].encode('latin1')
            stored_signature = payload['signature']

            decrypted_bytes = self.cipher.decrypt(encrypted_data)
            decrypted_json = decrypted_bytes.decode('utf-8')
            decrypted_data = json.loads(decrypted_json)
            # Verify signature
            current_signature = hmac.new(
                self.signature_key,
                json.dumps(decrypted_data, sort_keys=True).encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            if current_signature != stored_signature:
                raise ValueError("File has been tampered with")

            return decrypted_data

        except (SyntaxError, NameError, TypeError, ValueError, FileNotFoundError) as e:
            print(f"Decryption error : {e}")
            return []

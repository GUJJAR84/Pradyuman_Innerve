"""
Credential Manager - Secure storage of platform credentials

Handles encryption and decryption of social media credentials
using AES-128 encryption. Only decrypts after voice authentication.
"""

import json
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Manages encrypted storage of platform credentials
    """
    
    def __init__(self, credentials_dir="credentials", keys_dir="keys"):
        self.credentials_dir = Path(credentials_dir)
        self.keys_dir = Path(keys_dir)
        
        # Create directories if they don't exist
        self.credentials_dir.mkdir(exist_ok=True)
        self.keys_dir.mkdir(exist_ok=True)
        
        logger.info("Credential Manager initialized")
    
    def add_credential(self, platform: str, username: str, password: str, owner: str) -> bool:
        """
        Encrypts and saves credentials for a platform
        
        Args:
            platform: Platform name (e.g., "Instagram", "Gmail")
            username: Account username
            password: Account password
            owner: Voice-authenticated user who owns this credential
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # 1. Create credential object
            credential_data = {
                "platform": platform,
                "username": username,
                "password": password,
                "owner": owner,
                "added_at": datetime.now().isoformat()
            }
            
            # 2. Convert to JSON string
            json_data = json.dumps(credential_data)
            plaintext = json_data.encode('utf-8')
            
            # 3. Generate random encryption key (128 bits = 16 bytes)
            key = os.urandom(16)
            
            # 4. Generate random IV (initialization vector)
            iv = os.urandom(16)
            
            # 5. Pad data to AES block size (16 bytes)
            padded_data = self._pad(plaintext)
            
            # 6. Encrypt with AES-128-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # 7. Generate HMAC for integrity verification
            h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
            h.update(ciphertext)
            mac = h.finalize()
            
            # 8. Save encrypted credentials (IV + ciphertext + HMAC)
            cred_file = self.credentials_dir / f"{platform.lower()}_{owner}.enc"
            with open(cred_file, 'wb') as f:
                f.write(iv)          # 16 bytes
                f.write(ciphertext)  # Variable length
                f.write(mac)         # 32 bytes
            
            # 9. Save encryption key separately
            key_file = self.keys_dir / f"{platform.lower()}_{owner}.key"
            with open(key_file, 'wb') as f:
                f.write(key)
            
            logger.info(f"✅ Saved encrypted credentials for {platform} ({owner})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save credentials: {e}")
            return False
    
    def get_credential(self, platform: str, owner: str) -> dict:
        """
        Decrypts and returns credentials for a platform
        
        IMPORTANT: Only call this AFTER voice authentication succeeds!
        
        Args:
            platform: Platform name (e.g., "Instagram")
            owner: Voice-authenticated user
            
        Returns:
            {"username": "...", "password": "..."}
            
        Raises:
            FileNotFoundError: If credentials don't exist
            ValueError: If decryption fails or HMAC verification fails
        """
        try:
            # 1. Load encryption key
            key_file = self.keys_dir / f"{platform.lower()}_{owner}.key"
            if not key_file.exists():
                raise FileNotFoundError(f"No credentials found for {platform}")
            
            with open(key_file, 'rb') as f:
                key = f.read()
            
            # 2. Load encrypted credentials
            cred_file = self.credentials_dir / f"{platform.lower()}_{owner}.enc"
            with open(cred_file, 'rb') as f:
                encrypted_data = f.read()
            
            # 3. Extract components (IV + ciphertext + HMAC)
            iv = encrypted_data[:16]
            mac = encrypted_data[-32:]
            ciphertext = encrypted_data[16:-32]
            
            # 4. Verify HMAC (integrity check)
            h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
            h.update(ciphertext)
            try:
                h.verify(mac)
            except Exception:
                raise ValueError("HMAC verification failed - data may be corrupted!")
            
            # 5. Decrypt with AES-128-CBC
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 6. Remove padding
            plaintext = self._unpad(padded_plaintext)
            
            # 7. Parse JSON
            json_data = plaintext.decode('utf-8')
            credential_data = json.loads(json_data)
            
            logger.info(f"🔓 Decrypted credentials for {platform}")
            
            # 8. Return only username and password (not metadata)
            return {
                "username": credential_data["username"],
                "password": credential_data["password"]
            }
            
        except FileNotFoundError as e:
            logger.error(f"❌ Credentials not found: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to decrypt credentials: {e}")
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def list_credentials(self, owner: str) -> list:
        """
        Lists all saved platforms for a user
        
        Args:
            owner: Voice-authenticated user
            
        Returns:
            List of platform names, e.g., ["Instagram", "Gmail", "Twitter"]
        """
        platforms = []
        for cred_file in self.credentials_dir.glob(f"*_{owner}.enc"):
            # Extract platform name from filename
            # Format: instagram_preet.enc -> Instagram
            platform = cred_file.stem.split('_')[0].capitalize()
            platforms.append(platform)
        
        logger.info(f"Found {len(platforms)} saved credentials for {owner}")
        return platforms
    
    def delete_credential(self, platform: str, owner: str) -> bool:
        """
        Deletes saved credentials for a platform
        
        Args:
            platform: Platform name
            owner: Voice-authenticated user
            
        Returns:
            True if deleted, False if not found
        """
        try:
            cred_file = self.credentials_dir / f"{platform.lower()}_{owner}.enc"
            key_file = self.keys_dir / f"{platform.lower()}_{owner}.key"
            
            if cred_file.exists():
                cred_file.unlink()
            if key_file.exists():
                key_file.unlink()
            
            logger.info(f"🗑️ Deleted credentials for {platform}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete credentials: {e}")
            return False
    
    def _pad(self, data: bytes) -> bytes:
        """
        PKCS7 padding to make data multiple of 16 bytes
        
        Args:
            data: Data to pad
            
        Returns:
            Padded data
        """
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad(self, data: bytes) -> bytes:
        """
        Remove PKCS7 padding
        
        Args:
            data: Padded data
            
        Returns:
            Original data without padding
        """
        padding_length = data[-1]
        return data[:-padding_length]

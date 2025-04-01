from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import hashlib
from .threat_detection import ThreatDetector as EnhancedThreatDetector

class FileEncryptor:
    """Handles encryption and decryption of files using AES-256 in CBC mode"""
    
    @staticmethod
    def generate_key():
        """Generate a secure random encryption key"""
        return os.urandom(32)  # 256 bits for AES-256
    
    @staticmethod
    def generate_iv():
        """Generate a secure random initialization vector"""
        return os.urandom(16)  # 128 bits for AES block size
    
    @staticmethod
    def encrypt_file(file_data, key, iv):
        """Encrypt file data using AES-256 in CBC mode"""
        # Create a padder to ensure the data is a multiple of the block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(file_data) + padder.finalize()
        
        # Create an encryptor object
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Encrypt the padded data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return encrypted_data
    
    @staticmethod
    def decrypt_file(encrypted_data, key, iv):
        """Decrypt file data using AES-256 in CBC mode"""
        # Create a decryptor object
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        original_data = unpadder.update(padded_data) + unpadder.finalize()
        
        return original_data

class ThreatDetector:
    """Implements zero-day threat detection for uploaded files
    
    This class is a wrapper around the enhanced threat detection implementation
    in threat_detection.py. It provides backward compatibility while using
    the more sophisticated threat detection capabilities.
    """
    
    @staticmethod
    def scan_file(file_data, filename):
        """Scan a file for potential threats using the enhanced threat detector"""
        # Use the enhanced threat detector for more comprehensive scanning
        return EnhancedThreatDetector.scan_file(file_data, filename)
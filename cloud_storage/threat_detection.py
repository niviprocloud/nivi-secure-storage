from cryptography.hazmat.primitives import hashes
import os
import re
import magic
import hashlib
import logging

class ThreatDetector:
    """Enhanced zero-day threat detection for uploaded files"""
    
    # Known malicious file signatures (simplified for demonstration)
    MALWARE_SIGNATURES = [
        b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',  # EICAR test signature
        b'MZ.*PE\x00\x00',  # Common executable header pattern
        b'<script>.*?evil.*?</script>',  # Simplified malicious script pattern
    ]
    
    # File types that require extra scrutiny
    HIGH_RISK_EXTENSIONS = [
        '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.msi',
        '.scr', '.hta', '.com', '.pif', '.reg', '.vbe', '.wsf', '.wsh'
    ]
    
    # Allowed media file extensions
    ALLOWED_MEDIA_EXTENSIONS = [
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
        # Audio
        '.mp3', '.wav', '.ogg', '.m4a', '.aac',
        # Video
        '.mp4', '.webm', '.avi', '.mov', '.mkv'
    ]
    
    # MIME types that require extra scrutiny
    HIGH_RISK_MIME_TYPES = [
        'application/x-msdownload',
        'application/x-executable',
        'application/x-dosexec',
        'application/x-msdos-program',
        'application/x-ms-shortcut'
    ]
    
    # Allowed media MIME types
    ALLOWED_MEDIA_MIME_TYPES = [
        # Images
        'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml',
        # Audio
        'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/aac',
        # Video
        'video/mp4', 'video/webm', 'video/x-msvideo', 'video/quicktime', 'video/x-matroska'
    ]
    
    @staticmethod
    def get_file_mime_type(file_data):
        """Determine the MIME type of a file based on its content"""
        try:
            mime = magic.Magic(mime=True)
            return mime.from_buffer(file_data[:4096])  # Only check the first 4KB for efficiency
        except ImportError:
            # Fallback if python-magic is not installed
            return None
    
    @staticmethod
    def check_file_signatures(file_data):
        """Check file against known malicious signatures"""
        threats = []
        
        # Convert file data to string for pattern matching if needed
        try:
            file_str = file_data.decode('utf-8', errors='ignore')
        except:
            file_str = str(file_data)
        
        # Check for known malicious patterns
        for signature in ThreatDetector.MALWARE_SIGNATURES:
            try:
                if isinstance(signature, bytes):
                    if signature in file_data:
                        threats.append({
                            'type': 'signature',
                            'severity': 'critical',
                            'message': 'Known malicious signature detected'
                        })
                else:
                    pattern = re.compile(signature, re.IGNORECASE | re.DOTALL)
                    if pattern.search(file_str):
                        threats.append({
                            'type': 'signature',
                            'severity': 'critical',
                            'message': 'Known malicious pattern detected'
                        })
            except Exception as e:
                logging.error(f"Error checking signature: {e}")
        
        return threats
    
    @staticmethod
    def analyze_file_content(file_data, filename):
        """Analyze file content for suspicious patterns"""
        threats = []
        
        # Check file size (unusually large files might be suspicious)
        if len(file_data) > 500 * 1024 * 1024:  # 500 MB
            threats.append({
                'type': 'size',
                'severity': 'warning',
                'message': 'File is unusually large'
            })
        
        # Check file extension
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext in ThreatDetector.HIGH_RISK_EXTENSIONS:
            threats.append({
                'type': 'filetype',
                'severity': 'critical',
                'message': f'This file type ({file_ext}) is not allowed as it may contain executable code.'
            })
        elif file_ext not in ThreatDetector.ALLOWED_MEDIA_EXTENSIONS:
            threats.append({
                'type': 'filetype',
                'severity': 'warning',
                'message': f'This file type ({file_ext}) is not in the list of allowed media files.'
            })
        
        # Check MIME type
        mime_type = ThreatDetector.get_file_mime_type(file_data)
        if mime_type:
            if mime_type in ThreatDetector.HIGH_RISK_MIME_TYPES:
                threats.append({
                    'type': 'mimetype',
                    'severity': 'critical',
                    'message': f'This file type ({mime_type}) is not allowed as it may contain executable content.'
                })
            elif mime_type not in ThreatDetector.ALLOWED_MEDIA_MIME_TYPES:
                threats.append({
                    'type': 'mimetype',
                    'severity': 'warning',
                    'message': f'This file type ({mime_type}) is not in the list of allowed media types.'
                })
        
        # Check for suspicious content patterns only for text-based files
        mime_type = ThreatDetector.get_file_mime_type(file_data)
        if mime_type and mime_type.startswith('text/') or mime_type == 'application/json' or mime_type == 'application/xml':
            try:
                file_str = file_data.decode('utf-8', errors='ignore')
                
                # Check for potential script injection
                if '<script>' in file_str.lower() and ('eval(' in file_str.lower() or 'document.cookie' in file_str.lower()):
                    threats.append({
                        'type': 'content',
                        'severity': 'high',
                        'message': 'Potential malicious script detected'
                    })
                    
                # Check for potential command injection
                if any(cmd in file_str.lower() for cmd in ['cmd.exe', 'powershell', 'wget ', 'curl ', '&&', '|', ';']):
                    threats.append({
                        'type': 'content',
                        'severity': 'high',
                        'message': 'Potential command injection detected'
                    })
            except:
                logging.warning(f"Failed to decode text content for file: {filename}")
                pass
        
        return threats
    
    @staticmethod
    def calculate_file_hash(file_data):
        """Calculate multiple hashes for the file"""
        md5 = hashlib.md5(file_data).hexdigest()
        sha1 = hashlib.sha1(file_data).hexdigest()
        sha256 = hashlib.sha256(file_data).hexdigest()
        
        return {
            'md5': md5,
            'sha1': sha1,
            'sha256': sha256
        }
    
    @staticmethod
    def scan_file(file_data, filename):
        """Comprehensive file scanning for potential threats
        
        This implementation includes multiple layers of threat detection:
        1. File signature analysis
        2. Content analysis
        3. File type verification
        4. Hash calculation for potential blacklist checking
        """
        all_threats = []
        
        # Check file signatures
        signature_threats = ThreatDetector.check_file_signatures(file_data)
        all_threats.extend(signature_threats)
        
        # Analyze file content
        content_threats = ThreatDetector.analyze_file_content(file_data, filename)
        all_threats.extend(content_threats)
        
        # Calculate file hashes
        file_hashes = ThreatDetector.calculate_file_hash(file_data)
        
        # In a production environment, you would check these hashes against
        # known malware databases or threat intelligence feeds
        
        # Determine overall threat level
        is_safe = True
        severity = 'safe'
        
        if all_threats:
            # Only mark as unsafe if there are critical or high severity threats
            critical_threats = [t for t in all_threats if t.get('severity') == 'critical']
            high_threats = [t for t in all_threats if t.get('severity') == 'high']
            
            if critical_threats:
                is_safe = False
                severity = 'critical'
            elif high_threats:
                is_safe = False
                severity = 'high'
            else:
                # Files with only warnings are considered safe
                severity = 'warning'
                is_safe = True
        
        return {
            'threats': all_threats,
            'file_hashes': file_hashes,
            'is_safe': is_safe,
            'severity': severity
        }
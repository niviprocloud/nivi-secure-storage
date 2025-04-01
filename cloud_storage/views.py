from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

from .models import EncryptedFile, SecurityLog
from .forms import FileUploadForm
from .encryption import FileEncryptor, ThreatDetector

import os
import mimetypes

# Helper function to log security events
def log_security_event(request, event_type, level, message, file=None):
    """Log a security event to the database"""
    SecurityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        event_type=event_type,
        level=level,
        message=message,
        file=file
    )

def home(request):
    """Home page view"""
    return render(request, 'cloud_storage/home.html')

@login_required
def dashboard(request):
    """User dashboard showing their encrypted files"""
    user_files = EncryptedFile.objects.filter(user=request.user).order_by('-upload_date')
    
    # Log dashboard access
    log_security_event(
        request, 
        'SYSTEM', 
        'INFO', 
        f'User {request.user.username} accessed their dashboard'
    )
    
    return render(request, 'cloud_storage/dashboard.html', {
        'user_files': user_files,
        'upload_form': FileUploadForm()
    })

@login_required
def upload_file(request):
    """Handle file uploads, encryption, and threat detection"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Read file data
            file_data = uploaded_file.read()
            
            # Scan for threats with enhanced threat detection
            scan_result = ThreatDetector.scan_file(file_data, uploaded_file.name)
            
            if not scan_result['is_safe']:
                # Log the threat with appropriate severity level
                severity = scan_result.get('severity', 'WARNING').upper()
                if severity not in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                    severity = 'WARNING'
                
                # Create detailed threat message
                threat_details = '\n'.join([f"- {t.get('type', 'unknown')}: {t.get('message', 'Unknown threat')}" 
                                           for t in scan_result['threats']])
                threat_message = f"Potential threat detected in file {uploaded_file.name}:\n{threat_details}"
                
                # Log with file hash information for future reference
                hash_info = f"File hashes: {scan_result.get('file_hashes', {})}"
                full_message = f"{threat_message}\n{hash_info}"
                
                log_security_event(
                    request, 
                    'THREAT', 
                    severity, 
                    full_message
                )
                
                messages.error(request, "This file may contain security threats and cannot be uploaded.")
                return redirect('dashboard')
            
            # Generate encryption key and IV
            key = FileEncryptor.generate_key()
            iv = FileEncryptor.generate_iv()
            
            # Encrypt the file
            encrypted_data = FileEncryptor.encrypt_file(file_data, key, iv)
            
            # Create the EncryptedFile record
            encrypted_file = EncryptedFile(
                user=request.user,
                original_filename=uploaded_file.name,
                file_size=len(file_data),
                content_type=uploaded_file.content_type or 'application/octet-stream',
                encryption_key=key,
                iv=iv
            )
            encrypted_file.save()
            
            # Ensure user directory exists
            user_dir = os.path.join(settings.ENCRYPTED_FILES_ROOT, str(request.user.id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Save the encrypted file to disk
            file_path = encrypted_file.get_file_path()
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Log the upload
            log_security_event(
                request, 
                'UPLOAD', 
                'INFO', 
                f'User {request.user.username} uploaded and encrypted file: {uploaded_file.name}',
                encrypted_file
            )
            
            messages.success(request, f"File {uploaded_file.name} has been securely uploaded and encrypted.")
            return redirect('dashboard')
    else:
        form = FileUploadForm()
    
    return render(request, 'cloud_storage/upload.html', {'form': form})

@login_required
def download_file(request, file_id):
    """Download and decrypt a file"""
    encrypted_file = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
    
    # Update last accessed time
    encrypted_file.last_accessed = timezone.now()
    encrypted_file.save(update_fields=['last_accessed'])
    
    # Get the file path
    file_path = encrypted_file.get_file_path()
    
    # Check if file exists
    if not os.path.exists(file_path):
        log_security_event(
            request, 
            'ERROR', 
            'ERROR', 
            f'File not found on disk: {encrypted_file.original_filename}',
            encrypted_file
        )
        raise Http404("File not found on the server.")
    
    # Read the encrypted file
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    # Decrypt the file
    try:
        decrypted_data = FileEncryptor.decrypt_file(
            encrypted_data, 
            encrypted_file.encryption_key, 
            encrypted_file.iv
        )
        
        # Log the download
        log_security_event(
            request, 
            'DOWNLOAD', 
            'INFO', 
            f'User {request.user.username} downloaded and decrypted file: {encrypted_file.original_filename}',
            encrypted_file
        )
        
        # Prepare the response
        response = HttpResponse(decrypted_data, content_type=encrypted_file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{encrypted_file.original_filename}"'
        return response
        
    except Exception as e:
        # Log the error
        log_security_event(
            request, 
            'ERROR', 
            'ERROR', 
            f'Error decrypting file {encrypted_file.original_filename}: {str(e)}',
            encrypted_file
        )
        messages.error(request, "Error decrypting the file. Please try again later.")
        return redirect('dashboard')

@login_required
@require_POST
def delete_file(request, file_id):
    """Delete an encrypted file"""
    encrypted_file = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
    
    # Get the file path
    file_path = encrypted_file.get_file_path()
    
    # Delete the file from disk if it exists
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Log the deletion
    log_security_event(
        request, 
        'DELETE', 
        'INFO', 
        f'User {request.user.username} deleted file: {encrypted_file.original_filename}',
        encrypted_file
    )
    
    # Delete the database record
    encrypted_file.delete()
    
    messages.success(request, f"File {encrypted_file.original_filename} has been deleted.")
    return redirect('dashboard')

def security_policy(request):
    """View for displaying the security policy"""
    return render(request, 'cloud_storage/security_policy.html')


def logout_view(request):
    """Custom logout view that handles user logout"""
    logout(request)
    return redirect('login')

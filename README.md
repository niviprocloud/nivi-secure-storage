# NiVi Secure Cloud Storage

A secure cloud storage solution with military-grade encryption, zero-day threat protection, and Google authentication.

## Features

- **AES-256 Encryption**: All files are encrypted with AES-256 before storage
- **Google OAuth2 Authentication**: Secure login using Google accounts
- **Zero-Day Threat Protection**: Advanced threat detection for uploaded files
- **Secure File Management**: Upload, download, and delete files securely
- **Security Logging**: Comprehensive security event logging

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip package manager
- A Google OAuth2 client ID and secret

### Installation

1. Clone the repository

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure Google OAuth2:
   - Create a project in the [Google Developer Console](https://console.developers.google.com/)
   - Enable the Google+ API
   - Create OAuth2 credentials (Web application type)
   - Set the redirect URI to `http://localhost:8000/oauth/complete/google-oauth2/`
   - Update the `nivi_project/oauth_settings.py` file with your client ID and secret

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at `http://localhost:8000`

## Usage

1. **Login**: Sign in with your Google account
2. **Dashboard**: View and manage your encrypted files
3. **Upload**: Upload files to be encrypted and stored securely
4. **Download**: Download and decrypt your files
5. **Delete**: Permanently remove files from storage

## Security Features

### Encryption
- Client-side encryption with AES-256
- Unique encryption key for each file
- Secure key storage

### Authentication
- Google OAuth2 for secure authentication
- Two-factor authentication through Google
- Secure session management

### Threat Protection
- File scanning for malicious content
- Signature-based threat detection
- Content analysis for suspicious patterns
- File type verification

### Security Logging
- Comprehensive logging of all security events
- Anomaly detection for unusual activities
- Security alerts for potential issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.
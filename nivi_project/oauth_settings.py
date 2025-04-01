# Google OAuth2 Configuration

# Instructions to set up Google OAuth2:
# 1. Go to https://console.developers.google.com/
# 2. Create a new project or select an existing one
# 3. Go to "Credentials" and click "Create credentials" > "OAuth client ID"
# 4. Select "Web application" as the application type
# 5. Add "http://127.0.0.1:8000" to Authorized JavaScript origins
# 6. Add "http://127.0.0.1:8000/oauth/complete/google-oauth2/" to Authorized redirect URIs (must include trailing slash)
#    IMPORTANT: The trailing slash is required! Make sure the URI in Google Cloud Console
#    exactly matches the URI that social-auth-app-django generates
# 7. Click "Create" and copy your Client ID and Client Secret below

import os

# OAuth credentials from environment variables
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# Scopes required for the application
GOOGLE_OAUTH2_SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

# Redirect URI after successful authentication
# Note: The social-auth-app-django package automatically generates the redirect URI
# based on the URL patterns and namespace configuration in urls.py.
# You don't need to specify the redirect URI in this file.
# Just make sure that the URI registered in Google Cloud Console exactly matches
# the URI that social-auth-app-django generates: http://127.0.0.1:8000/oauth/complete/google-oauth2/
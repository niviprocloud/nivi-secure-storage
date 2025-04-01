# NiVi Pro Deployment Guide

## Google Cloud Platform Setup

### 1. Database Setup (Cloud SQL - PostgreSQL)

1. Create a new Cloud SQL instance:
   - Go to Google Cloud Console > SQL
   - Create Instance > Choose PostgreSQL
   - Set instance ID and password
   - Choose your region (preferably close to your target audience)

2. Configure database:
   - Create database: `nivi_db`
   - Create user: `nivi_user`
   - Set up strong password
   - Note down connection details

### 2. VM Instance Setup

1. Create a Compute Engine VM:
   - Go to Compute Engine > VM instances
   - Create Instance
   - Choose e2-micro (free tier eligible)
   - Select Ubuntu 20.04 LTS
   - Allow HTTP/HTTPS traffic

2. Set up VM:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y

   # Install required packages
   sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y

   # Clone your repository
   git clone <your-repo-url>
   cd your-project

   # Set up virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### 3. Domain Configuration

1. Configure DNS:
   - Add A record pointing to your VM's IP
   - Add CNAME record for www subdomain

2. SSL Setup:
   ```bash
   sudo certbot --nginx -d nivipro.in -d www.nivipro.in
   ```

### 4. Nginx Configuration

1. Create Nginx config:
   ```nginx
   server {
       server_name nivipro.in www.nivipro.in;
       
       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /path/to/your/project;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/run/gunicorn.sock;
       }

       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/nivipro.in/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/nivipro.in/privkey.pem;
   }
   ```

### 5. Gunicorn Setup

1. Create systemd service:
   ```bash
   sudo nano /etc/systemd/system/gunicorn.service
   ```

   ```ini
   [Unit]
   Description=gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock nivi_project.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

### 6. Final Steps

1. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

2. Apply migrations:
   ```bash
   python manage.py migrate
   ```

3. Start services:
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   sudo systemctl restart nginx
   ```

### 7. Maintenance

- Set up regular backups for your database
- Monitor your application logs
- Keep your dependencies updated
- Regularly update SSL certificates (automatic with certbot)

## Important Notes

- Keep your .env file secure and never commit it to version control
- Regularly rotate your database passwords and secret keys
- Monitor your Google Cloud Console for usage and billing
- The free tier includes many services but has limits, monitor your usage
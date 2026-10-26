#!/bin/bash
set -e

echo "Updating packages..."
sudo apt update

echo "Installing Nginx, Certbot, and Gunicorn..."
sudo apt install -y nginx certbot python3-certbot-nginx gunicorn

echo "Copying systemd service and socket files..."
sudo cp /home/ubuntu/deploy/systemd/portfolio.socket /etc/systemd/system/
sudo cp /home/ubuntu/deploy/systemd/portfolio.service /etc/systemd/system/

echo "Reloading systemd and enabling portfolio service..."
sudo systemctl daemon-reload
sudo systemctl start portfolio.socket
sudo systemctl enable portfolio.socket
sudo systemctl restart portfolio.service

echo "Setting up Nginx..."
sudo cp /home/ubuntu/deploy/nginx/portfolio.conf /etc/nginx/sites-available/portfolio
sudo ln -sf /etc/nginx/sites-available/portfolio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

echo "Testing Nginx configuration..."
sudo nginx -t

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Obtaining SSL certificate with Let's Encrypt..."
# Note: This will automatically update the Nginx configuration to include SSL settings
sudo certbot --nginx -d markocampos.duckdns.org --non-interactive --agree-tos -m markocampos.mail@gmail.com --redirect

echo "Collecting static files for Django..."
cd /home/ubuntu/portfolio
python3 manage.py collectstatic --noinput

echo "Setting permissions for static files..."
sudo chown -R ubuntu:www-data /home/ubuntu/portfolio/staticfiles
sudo chmod -R 755 /home/ubuntu/portfolio/staticfiles

echo "Restarting Nginx and Gunicorn to apply all changes..."
sudo systemctl restart portfolio
sudo systemctl restart nginx

echo "Setup complete! The site should now be securely available at https://markocampos.duckdns.org"

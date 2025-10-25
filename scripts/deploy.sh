#!/bin/bash
# BJJ CRM Deployment Script for Ubuntu Server
# Usage: ./deploy.sh

set -e

echo "🚀 Starting BJJ CRM deployment on Ubuntu server..."

# Server configuration
SERVER_IP="193.222.96.161"
SERVER_USER="root"
SERVER_PASSWORD="<DaVinci&&2025/>"
APP_DIR="/opt/bjj_crm"
SERVICE_NAME="bjj-crm"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    print_error "sshpass is not installed. Please install it first:"
    echo "brew install hudochenkov/sshpass/sshpass"
    exit 1
fi

# Function to execute commands on remote server
execute_remote() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
}

# Function to copy files to remote server
copy_to_remote() {
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" "$SERVER_USER@$SERVER_IP:$2"
}

print_status "Connecting to server $SERVER_IP..."

# Update system packages
print_status "Updating system packages..."
execute_remote "apt update && apt upgrade -y"

# Install Python 3 and pip
print_status "Installing Python 3 and pip..."
execute_remote "apt install -y python3 python3-pip python3-venv python3-tk"

# Install PostgreSQL
print_status "Installing PostgreSQL..."
execute_remote "apt install -y postgresql postgresql-contrib"

# Configure PostgreSQL
print_status "Configuring PostgreSQL..."
execute_remote "sudo -u postgres psql -c \"CREATE DATABASE bjj_crm;\""
execute_remote "sudo -u postgres psql -c \"CREATE USER bjj_user WITH PASSWORD 'bjj_password123';\""
execute_remote "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE bjj_crm TO bjj_user;\""

# Create application directory
print_status "Creating application directory..."
execute_remote "mkdir -p $APP_DIR"

# Copy application files
print_status "Copying application files..."
copy_to_remote "." "$APP_DIR/"

# Create virtual environment on server
print_status "Creating virtual environment on server..."
execute_remote "cd $APP_DIR && python3 -m venv venv"

# Install dependencies
print_status "Installing Python dependencies..."
execute_remote "cd $APP_DIR && source venv/bin/activate && pip install -r requirements.txt"

# Update database configuration for PostgreSQL
print_status "Updating database configuration..."
execute_remote "cd $APP_DIR && echo 'DATABASE_URL=postgresql://bjj_user:bjj_password123@localhost/bjj_crm' > .env"

# Initialize database
print_status "Initializing database..."
execute_remote "cd $APP_DIR && source venv/bin/activate && python scripts/init_db.py"

# Create systemd service
print_status "Creating systemd service..."
execute_remote "cat > /etc/systemd/system/$SERVICE_NAME.service << 'EOF'
[Unit]
Description=BJJ Academy CRM System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# Enable and start service
print_status "Enabling and starting service..."
execute_remote "systemctl daemon-reload"
execute_remote "systemctl enable $SERVICE_NAME"
execute_remote "systemctl start $SERVICE_NAME"

# Check service status
print_status "Checking service status..."
execute_remote "systemctl status $SERVICE_NAME --no-pager"

# Create backup script
print_status "Creating backup script..."
execute_remote "cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=\"/opt/backups/bjj_crm\"
DATE=\$(date +%Y%m%d_%H%M%S)
mkdir -p \$BACKUP_DIR

# Backup database
pg_dump -h localhost -U bjj_user bjj_crm > \$BACKUP_DIR/bjj_crm_\$DATE.sql

# Backup application files
tar -czf \$BACKUP_DIR/bjj_crm_files_\$DATE.tar.gz -C /opt bjj_crm

# Keep only last 7 days of backups
find \$BACKUP_DIR -name \"*.sql\" -mtime +7 -delete
find \$BACKUP_DIR -name \"*.tar.gz\" -mtime +7 -delete

echo \"Backup completed: \$DATE\"
EOF"

execute_remote "chmod +x $APP_DIR/backup.sh"

# Setup cron job for daily backups
print_status "Setting up daily backups..."
execute_remote "echo '0 2 * * * $APP_DIR/backup.sh' | crontab -"

print_status "🎉 Deployment completed successfully!"
print_status "Application is running on server $SERVER_IP"
print_status "Service status: systemctl status $SERVICE_NAME"
print_status "Logs: journalctl -u $SERVICE_NAME -f"
print_status "Backup script: $APP_DIR/backup.sh"

echo ""
print_status "Next steps:"
echo "1. Configure Telegram bot token in $APP_DIR/.env"
echo "2. Configure Google Calendar integration"
echo "3. Test the application functionality"
echo "4. Set up monitoring and alerts"

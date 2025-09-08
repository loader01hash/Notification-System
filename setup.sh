#!/bin/bash

# Django Notification System Setup Script

echo "🚀 Setting up Django Notification System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements/development.txt

# Copy environment file
echo "⚙️ Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "📝 Please edit .env file with your configuration"
else
    echo "ℹ️ .env file already exists"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 Creating superuser..."
echo "You can skip this step by pressing Ctrl+C"
python manage.py createsuperuser || echo "Skipped superuser creation"

# Create default notification templates
echo "📧 Creating default notification templates..."
python manage.py create_templates

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Edit .env file with your Telegram bot token and email settings"
echo "2. Start Redis server: redis-server"
echo "3. Start Celery worker: celery -A config worker -l info"
echo "4. Start Django server: python manage.py runserver"
echo ""
echo "🐳 Or use Docker:"
echo "docker-compose up --build"
echo ""
echo "📖 Check README.md for more detailed instructions"

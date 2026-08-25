#!/bin/bash
echo "🚀 Starting NHS Personalised Care Server"
echo "========================================="

# Check for Python 3.10
echo "Checking Python version..."

if command -v python3.10 &> /dev/null; then
    echo "✅ Python 3.10 found"
    PYTHON_CMD="python3.10"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if [[ "$PYTHON_VERSION" == "3.10" ]]; then
        echo "✅ Python 3.10 found"
        PYTHON_CMD="python3"
    else
        echo "⚠️  Python version: $PYTHON_VERSION (3.10 recommended)"
        echo "   Trying to continue with $PYTHON_VERSION..."
        PYTHON_CMD="python3"
    fi
else
    echo "❌ Python not found!"
    echo "Please install Python 3.10 from: https://www.python.org/downloads/"
    exit 1
fi

echo "Using: $PYTHON_CMD"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies with retry
echo "📦 Installing dependencies..."
for i in {1..3}; do
    echo "Attempt $i..."
    pip install -r requirements.txt && break
    if [ $i -eq 3 ]; then
        echo "❌ Failed after 3 attempts. Installing without cache..."
        pip install --no-cache-dir -r requirements.txt
        if [ $? -ne 0 ]; then
            echo "💡 Please install manually:"
            echo "   pip install flask flask-cors flask-socketio pandas numpy scikit-learn Pillow"
            exit 1
        fi
    fi
done

# Create directories
mkdir -p static/icons templates

# Generate icons
if [ ! -f "static/icons/icon-192.png" ]; then
    echo "🎨 Generating icons..."
    $PYTHON_CMD generate_icons.py
fi

# Run server
echo "🏥 Starting server..."
$PYTHON_CMD nhs_care_server.py
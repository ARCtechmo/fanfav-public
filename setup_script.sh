#!/bin/bash

# ------------------------------
# Fanfav Setup Script (Git Bash)
# ------------------------------
echo "🚀 Starting Fanfav project setup..."

# Check for Git
if command -v git &> /dev/null; then
    echo "✅ Git is installed: $(git --version)"
else
    echo "❌ Git is not installed. Please install it from https://git-scm.com/downloads"
    exit 1
fi

# Check for Python
if command -v python &> /dev/null; then
    echo "✅ Python is installed: $(python --version)"
else
    echo "❌ Python is not installed. Please install Anaconda from https://www.anaconda.com/download/success"
    exit 1
fi

# Clone repo if not already present
if [ ! -d "fanfav-public" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/ARCtechmo/fanfav-public.git
else
    echo "📁 'fanfav-public' folder already exists. Skipping clone."
fi

cd fanfav-public || {
    echo "❌ Failed to enter fanfav-public directory. Exiting."
    exit 1
}

# Pull latest version
echo "🔄 Pulling latest updates..."
git pull origin main

# Check for requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python packages..."
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found. Please check your repository setup."
    exit 1
fi

# List notebooks in order
echo "📝 Notebooks should be run in the following order:"

echo "\n🥇 Core DataFrame Build Notebooks:"
echo "  - wr_df.ipynb"
echo "  - te_df.ipynb"
echo "  - rb_df.ipynb"
echo "  - qb_df.ipynb"
echo "  - team_df.ipynb"

echo "\n🥈 Feature Engineering & Prep Notebooks:"
echo "  - wr_eda_modeling_prep.ipynb"
echo "  - te_eda_modeling_prep.ipynb"
echo "  - rb_eda_modeling_prep.ipynb"
echo "  - qb_eda_modeling_prep.ipynb"
echo "  - team_eda_modeling_prep.ipynb"

echo "💡 Launch Jupyter Notebook from Anaconda Navigator or Anaconda Prompt to begin."

echo "✅ Setup complete!"
echo ""
echo "📌 To make this script executable in Git Bash, run:"
echo "  chmod +x setup_script.sh"
echo ""
echo "▶️ Then run it with:"
echo "  ./setup_script.sh"
echo ""
echo "This script provides the easiest and fastest way to install and configure the project. For manual setup, refer to the INSTALLATION_GUIDE.md file."

exit 0

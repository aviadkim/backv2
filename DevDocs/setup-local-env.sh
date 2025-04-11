#!/bin/bash
# Bash script to set up local development environment

# Create .env file for local development
echo "Setting up local development environment..."

# Check if .env file already exists
if [ -f ".env" ]; then
    read -p ".env file already exists. Overwrite? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Ask for API keys
read -p "Enter your OpenRouter API Key: " openRouterApiKey
read -p "Enter your Supabase URL (e.g., https://your-project-id.supabase.co): " supabaseUrl
read -p "Enter your Supabase Key: " supabaseKey

# Create .env file
cat > .env << EOL
# Local development environment variables
# DO NOT COMMIT THIS FILE TO VERSION CONTROL

# Supabase configuration
SUPABASE_URL=$supabaseUrl
SUPABASE_KEY=$supabaseKey

# OpenRouter API key
OPENROUTER_API_KEY=$openRouterApiKey

# Node environment
NODE_ENV=development
EOL

echo "Local environment setup complete!"
echo "The .env file has been created with your API keys."
echo "IMPORTANT: Do not commit the .env file to version control."

# Add .env to .gitignore if it's not already there
if ! grep -q "^.env$" .gitignore 2>/dev/null; then
    echo "Adding .env to .gitignore..."
    echo -e "\n# Local environment variables\n.env" >> .gitignore
fi

# Install dependencies
read -p "Install dependencies? (y/n): " installDeps
if [ "$installDeps" = "y" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Setup complete! You can now run 'npm run dev' to start the development server."

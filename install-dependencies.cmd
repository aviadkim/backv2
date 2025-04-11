@echo off
echo Installing all dependencies for the project...

echo Installing Python dependencies...
python -m pip install -r requirements.txt

echo Installing Node dependencies...
npm install

echo Installing DevDocs dependencies...
cd DevDocs
npm install
cd ..

echo Installing Playwright dependencies...
cd DevDocs
npx playwright install
cd ..

echo Dependencies installed successfully!
pause

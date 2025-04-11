# Flask API Troubleshooting Guide

## Common Issues and Solutions

### 404 Not Found for All Routes

This usually indicates one of these issues:

1. **Flask app is not running**
   - Run `python app.py` and check for error messages

2. **Route definitions are not working**
   - Run `python debug_routes.py` to see all registered routes
   - Check that routes are properly defined with the correct decorator

3. **Port issues**
   - Try using a different port by changing the port value in app.py
   - Check if anything else is using port 24125

### Testing the API step-by-step

1. **Test with minimal setup**
   ```
   python simple_server.py
   ```
   Then try accessing http://localhost:24125/ and http://localhost:24125/api/health

2. **Test with curl or similar tool**
   ```
   curl http://localhost:24125/api/health
   ```

3. **Check if Flask is running with the right host**
   - Make sure app.run has host='0.0.0.0' to allow external access

4. **Test direct Python request**
   ```python
   import requests
   print(requests.get('http://localhost:24125/').text)
   ```

### Advanced Troubleshooting

1. **Manual Flask debugging**
   ```python
   from flask import Flask
   app = Flask(__name__)
   print(app.url_map)  # See all routes
   ```

2. **Environment issues**
   - Check Python version: `python --version`
   - Verify Flask is installed: `pip show flask`

3. **Debug mode**
   - Set debug=True in app.run()
   - Set FLASK_DEBUG=1 in environment
   
4. **Network access**
   - Check if the port is accessible: `netstat -an | findstr 24125`
   - Check if firewall is blocking: temporarily disable firewall

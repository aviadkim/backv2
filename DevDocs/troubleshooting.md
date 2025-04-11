# DevDocs Troubleshooting Guide

## API Connection Issues

### Problem: 404 Not Found errors when accessing API endpoints

**Possible causes and solutions:**

1. **Backend server is not running**
   - Verify the backend server is running: `cd backend && python app.py`
   - Check for error messages in the terminal where Flask is running

2. **Port conflict**
   - Check if port 24125 is already in use: `netstat -ano | findstr :24125`
   - If in use, terminate the process or change the port in app.py

3. **CORS issues**
   - Open browser developer console to check for CORS errors
   - Verify the CORS configuration in app.py

4. **Routes defined incorrectly**
   - Verify route definitions in app.py match the expected endpoints
   - Ensure Flask app is properly configured

### Problem: API connection timing out

**Possible causes and solutions:**

1. **Firewall blocking the connection**
   - Check Windows Firewall settings
   - Temporarily disable firewall for testing

2. **Network issues**
   - Try accessing the API from the same machine using localhost
   - Check if the machine is properly connected to the network

## Quick Fixes

### Restart both servers

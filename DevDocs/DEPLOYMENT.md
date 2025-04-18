# Deployment Guide for FinDoc Analyzer

This document provides instructions for deploying the FinDoc Analyzer application to Google Cloud Run using Docker and GitHub Actions.

## Prerequisites

- Google Cloud Platform account
- GitHub account
- Docker installed locally (for testing)
- Node.js and npm installed locally (for development)

## Environment Variables

The following environment variables are required for the application to function properly:

- `NODE_ENV`: Set to `production` for production deployment
- `OPENROUTER_API_KEY`: API key for OpenRouter AI services
- `JWT_SECRET`: Secret key for JWT authentication
- `ENCRYPTION_KEY`: Key for data encryption

## Local Development

1. Clone the repository:
   ```
   git clone https://github.com/aviadkim/backv2.git
   cd backv2
   ```

2. Install dependencies:
   ```
   cd DevDocs/frontend
   npm install
   cd ../backend
   npm install
   ```

3. Create a `.env` file in the `DevDocs/backend` directory with the required environment variables.

4. Start the backend server:
   ```
   cd DevDocs/backend
   node server.js
   ```

5. Start the frontend development server:
   ```
   cd DevDocs/frontend
   npm start
   ```

## Docker Deployment

1. Build the Docker image:
   ```
   docker build -t findoc-analyzer .
   ```

2. Run the Docker container locally:
   ```
   docker run -p 8080:8080 -e NODE_ENV=production -e OPENROUTER_API_KEY=your_key findoc-analyzer
   ```

## Google Cloud Run Deployment

### Manual Deployment

1. Build and push the Docker image to Google Container Registry:
   ```
   docker build -t gcr.io/your-project-id/findoc-analyzer .
   docker push gcr.io/your-project-id/findoc-analyzer
   ```

2. Deploy to Google Cloud Run:
   ```
   gcloud run deploy findoc-analyzer \
     --image gcr.io/your-project-id/findoc-analyzer \
     --platform managed \
     --region me-west1 \
     --allow-unauthenticated \
     --set-env-vars="NODE_ENV=production,OPENROUTER_API_KEY=your_key"
   ```

### Automated Deployment with GitHub Actions

The repository is configured with GitHub Actions for continuous integration and deployment. When you push changes to the `main` branch, the following steps are automatically executed:

1. Code is checked out
2. Dependencies are installed
3. Tests are run
4. Docker image is built and pushed to Google Container Registry
5. Application is deployed to Google Cloud Run

To set up automated deployment:

1. Create a Google Cloud service account with the necessary permissions
2. Generate a JSON key for the service account
3. Add the following secrets to your GitHub repository:
   - `GCP_SA_KEY`: The JSON key for the service account
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `JWT_SECRET`: Secret key for JWT authentication
   - `ENCRYPTION_KEY`: Key for data encryption

## Monitoring and Maintenance

### Monitoring

- Use Google Cloud Monitoring to monitor the application's performance and health
- Set up alerts for high CPU usage, memory usage, and error rates
- Monitor API usage and costs

### Maintenance

- Regularly update dependencies to fix security vulnerabilities
- Monitor logs for errors and warnings
- Perform regular backups of the database
- Conduct security audits

## Troubleshooting

### Common Issues

1. **Application fails to start**
   - Check environment variables
   - Check logs for errors
   - Verify that all dependencies are installed

2. **API requests fail**
   - Check API key validity
   - Verify network connectivity
   - Check rate limits

3. **Performance issues**
   - Check CPU and memory usage
   - Optimize database queries
   - Implement caching for frequently accessed data

## Support

For support, please contact the development team at support@example.com.

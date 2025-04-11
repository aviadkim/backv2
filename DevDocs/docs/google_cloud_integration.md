# Google Cloud Integration Guide

This guide provides instructions for setting up the Google Cloud integration for DevDocs.

## Overview

DevDocs integrates with Google Cloud to provide advanced document processing capabilities:

1. **Google Cloud Storage**: Used to store uploaded documents
2. **Google Cloud Document AI**: Used to process and extract information from documents

## Prerequisites

- Google Cloud account
- Google Cloud project with Storage and Document AI APIs enabled
- Service account with appropriate permissions
- Document AI processor configured

## Setup Steps

### 1. Create a Google Cloud Project

If you don't already have a Google Cloud project, create one:

```bash
gcloud projects create your-project-id
```

### 2. Enable Required APIs

Enable the Storage and Document AI APIs:

```bash
gcloud services enable storage.googleapis.com documentai.googleapis.com
```

### 3. Create a Service Account

Create a service account for DevDocs:

```bash
gcloud iam service-accounts create devdocs-service-account
```

### 4. Grant Permissions

Grant the service account the necessary permissions:

```bash
# Storage Admin role
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:devdocs-service-account@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Document AI Admin role
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:devdocs-service-account@your-project-id.iam.gserviceaccount.com" \
  --role="roles/documentai.admin"
```

### 5. Create a Service Account Key

Create a key for the service account:

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=devdocs-service-account@your-project-id.iam.gserviceaccount.com
```

### 6. Create a Storage Bucket

Create a Google Cloud Storage bucket to store documents:

```bash
gsutil mb -p your-project-id -l us-central1 gs://your-storage-bucket
```

### 7. Make the Bucket Publicly Readable (Optional)

If you want the documents to be publicly accessible:

```bash
gsutil iam ch allUsers:objectViewer gs://your-storage-bucket
```

### 8. Create a Document AI Processor

Create a Document AI processor for document processing:

```bash
gcloud beta documentai processors create \
  --project=your-project-id \
  --location=us \
  --display-name="DevDocs Processor" \
  --type=FORM_PARSER_PROCESSOR
```

Note the processor ID that is returned.

## Configuration

### Environment Variables

Update your `.env.local` file with the following variables:

```
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_CLIENT_EMAIL=devdocs-service-account@your-project-id.iam.gserviceaccount.com
GOOGLE_CLOUD_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
GOOGLE_CLOUD_STORAGE_BUCKET=your-storage-bucket
GOOGLE_CLOUD_DOCUMENT_AI_PROCESSOR_ID=your-document-ai-processor-id
GOOGLE_CLOUD_DOCUMENT_AI_LOCATION=us
```

### Service Account Key

If you prefer to use a key file instead of environment variables:

1. Save the `key.json` file in a secure location
2. Update the `.env.local` file with the path to the key file:

```
GOOGLE_CLOUD_KEY_FILENAME=/path/to/key.json
```

## Testing the Integration

### Test Storage Integration

1. Navigate to the DevDocs page
2. Upload a document
3. Verify that the document is uploaded to Google Cloud Storage

### Test Document AI Integration

1. Upload a document
2. Wait for the document to be processed
3. View the document details to see the processing results

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check that the service account has the necessary permissions
2. **API Not Enabled**: Ensure that the Storage and Document AI APIs are enabled
3. **Invalid Credentials**: Verify that the service account key is correct
4. **Bucket Not Found**: Check that the storage bucket exists and is accessible
5. **Processor Not Found**: Verify that the Document AI processor ID is correct

### Checking Logs

Check the application logs for error messages:

```bash
docker logs devdocs-backend
```

### Verifying Configuration

Verify that the environment variables are correctly set:

```bash
docker exec devdocs-backend env | grep GOOGLE_CLOUD
```

## Security Considerations

1. **Service Account Key**: Keep the service account key secure and never commit it to version control
2. **Bucket Access**: Consider restricting access to the storage bucket
3. **Document AI Access**: Limit access to the Document AI processor
4. **Environment Variables**: Use environment variables instead of hardcoding credentials

## Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Google Cloud Document AI Documentation](https://cloud.google.com/document-ai/docs)
- [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)

const DevDocsGoogleCloudIntegration = require('./devdocs-integration');
const fs = require('fs');
const path = require('path');

// Initialize the DevDocs Google Cloud Integration
const integration = new DevDocsGoogleCloudIntegration();

// Example usage
async function runExample() {
  try {
    console.log('DevDocs Google Cloud Integration Example');
    console.log('----------------------------------------');

    // List buckets
    console.log('\n1. Listing storage buckets:');
    const buckets = await integration.listBuckets();
    console.log(buckets);

    // Use the first bucket or 'devdocs-bucket'
    const bucketName = buckets[0] || 'devdocs-bucket';
    console.log(`\nUsing bucket: ${bucketName}`);

    // List files in the bucket
    console.log('\n2. Listing files in the bucket:');
    const files = await integration.listFiles(bucketName);
    console.log(files);

    // Upload a sample file
    console.log('\n3. Uploading a sample file:');
    const sampleFileName = 'sample-doc.txt';
    const sampleContent = 'This is a sample document for DevDocs integration testing.';
    await integration.uploadFile(bucketName, sampleFileName, sampleContent);
    console.log(`File ${sampleFileName} uploaded successfully.`);

    // List files again to verify the upload
    console.log('\n4. Listing files after upload:');
    const updatedFiles = await integration.listFiles(bucketName);
    console.log(updatedFiles);

    // Download the file
    console.log('\n5. Downloading the sample file:');
    const downloadedContent = await integration.downloadFile(bucketName, sampleFileName);
    console.log(`Downloaded content: ${downloadedContent.toString()}`);

    // Web search example
    console.log('\n6. Performing a web search:');
    const searchResults = await integration.webSearch('Google Cloud DevDocs integration');
    console.log(searchResults);

    // Web fetch example
    console.log('\n7. Fetching content from a URL:');
    const fetchedContent = await integration.webFetch('https://cloud.google.com/');
    console.log(`Fetched title: ${fetchedContent.title}`);
    console.log(`Fetched content length: ${fetchedContent.content.length} characters`);

    console.log('\nExample completed successfully!');
  } catch (error) {
    console.error('Error running example:', error.message);
  }
}

// Run the example
runExample();

from flask import Blueprint, request, jsonify
import requests
import json
import base64
import os

# MCP server URL
MCP_SERVER_URL = os.environ.get('MCP_SERVER_URL', 'http://localhost:8080/mcp')

# Create a Blueprint for MCP routes
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

def mcp_request(action, parameters=None):
    """
    Make a request to the MCP server
    
    Args:
        action (str): The action to perform
        parameters (dict, optional): The parameters for the action
        
    Returns:
        dict: The response from the MCP server
    """
    if parameters is None:
        parameters = {}
        
    try:
        response = requests.post(
            MCP_SERVER_URL,
            json={
                'action': action,
                'parameters': parameters
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making MCP request for action {action}: {str(e)}")
        return {
            'success': False,
            'error': f"MCP request failed: {str(e)}"
        }

@mcp_bp.route('/buckets', methods=['GET'])
def list_buckets():
    """List all storage buckets in the Google Cloud project"""
    response = mcp_request('listBuckets')
    return jsonify(response)

@mcp_bp.route('/files/<bucket_name>', methods=['GET'])
def list_files(bucket_name):
    """List files in a storage bucket"""
    response = mcp_request('listFiles', {'bucketName': bucket_name})
    return jsonify(response)

@mcp_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file to a storage bucket"""
    data = request.json
    bucket_name = data.get('bucketName')
    file_name = data.get('fileName')
    file_content = data.get('fileContent')
    
    if not bucket_name or not file_name or not file_content:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters: bucketName, fileName, fileContent'
        }), 400
    
    response = mcp_request('uploadFile', {
        'bucketName': bucket_name,
        'fileName': file_name,
        'fileContent': file_content
    })
    return jsonify(response)

@mcp_bp.route('/download', methods=['POST'])
def download_file():
    """Download a file from a storage bucket"""
    data = request.json
    bucket_name = data.get('bucketName')
    file_name = data.get('fileName')
    
    if not bucket_name or not file_name:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters: bucketName, fileName'
        }), 400
    
    response = mcp_request('downloadFile', {
        'bucketName': bucket_name,
        'fileName': file_name
    })
    return jsonify(response)

@mcp_bp.route('/process-document', methods=['POST'])
def process_document():
    """Process a document using Document AI"""
    data = request.json
    bucket_name = data.get('bucketName')
    file_name = data.get('fileName')
    
    if not bucket_name or not file_name:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters: bucketName, fileName'
        }), 400
    
    response = mcp_request('processDocument', {
        'bucketName': bucket_name,
        'fileName': file_name
    })
    return jsonify(response)

@mcp_bp.route('/web-search', methods=['GET'])
def web_search():
    """Search the web for information"""
    query = request.args.get('query')
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Missing required parameter: query'
        }), 400
    
    response = mcp_request('webSearch', {'query': query})
    return jsonify(response)

@mcp_bp.route('/web-fetch', methods=['GET'])
def web_fetch():
    """Fetch content from a URL"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            'success': False,
            'error': 'Missing required parameter: url'
        }), 400
    
    response = mcp_request('webFetch', {'url': url})
    return jsonify(response)

@mcp_bp.route('/request', methods=['POST'])
def generic_request():
    """Make a generic request to the MCP server"""
    data = request.json
    action = data.get('action')
    parameters = data.get('parameters', {})
    
    if not action:
        return jsonify({
            'success': False,
            'error': 'Missing required parameter: action'
        }), 400
    
    response = mcp_request(action, parameters)
    return jsonify(response)

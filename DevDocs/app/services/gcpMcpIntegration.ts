/**
 * GCP MCP Integration Service
 * 
 * This service provides integration between the DevDocs application and the GCP MCP server,
 * allowing AI assistants to interact with Google Cloud resources and DevDocs functionality.
 */

import { devDocsService, DocumentType } from './devDocs';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

/**
 * GCP MCP Integration Service
 */
export class GcpMcpIntegration {
  private isRunning: boolean = false;
  private mcpServerProcess: any = null;

  /**
   * Start the GCP MCP server
   */
  async startMcpServer(): Promise<boolean> {
    if (this.isRunning) {
      console.log('GCP MCP server is already running');
      return true;
    }

    try {
      // Determine the script to run based on the platform
      const scriptPath = process.platform === 'win32'
        ? path.join(process.cwd(), 'mcp', 'start-gcp-mcp.bat')
        : path.join(process.cwd(), 'mcp', 'start-gcp-mcp.sh');

      // Make the script executable on Unix-based systems
      if (process.platform !== 'win32') {
        fs.chmodSync(scriptPath, '755');
      }

      // Start the MCP server process
      this.mcpServerProcess = exec(scriptPath, (error, stdout, stderr) => {
        if (error) {
          console.error(`Error starting GCP MCP server: ${error.message}`);
          this.isRunning = false;
          return;
        }
        if (stderr) {
          console.error(`GCP MCP server stderr: ${stderr}`);
        }
        console.log(`GCP MCP server stdout: ${stdout}`);
      });

      this.mcpServerProcess.on('exit', (code: number) => {
        console.log(`GCP MCP server exited with code ${code}`);
        this.isRunning = false;
        this.mcpServerProcess = null;
      });

      this.isRunning = true;
      console.log('GCP MCP server started successfully');
      return true;
    } catch (error) {
      console.error('Error starting GCP MCP server:', error);
      return false;
    }
  }

  /**
   * Stop the GCP MCP server
   */
  stopMcpServer(): boolean {
    if (!this.isRunning || !this.mcpServerProcess) {
      console.log('GCP MCP server is not running');
      return true;
    }

    try {
      // Kill the MCP server process
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${this.mcpServerProcess.pid} /f /t`);
      } else {
        this.mcpServerProcess.kill('SIGTERM');
      }

      this.isRunning = false;
      this.mcpServerProcess = null;
      console.log('GCP MCP server stopped successfully');
      return true;
    } catch (error) {
      console.error('Error stopping GCP MCP server:', error);
      return false;
    }
  }

  /**
   * Check if the GCP MCP server is running
   */
  isMcpServerRunning(): boolean {
    return this.isRunning;
  }

  /**
   * Get the status of the GCP MCP integration
   */
  getStatus(): { isRunning: boolean; processId: number | null } {
    return {
      isRunning: this.isRunning,
      processId: this.mcpServerProcess ? this.mcpServerProcess.pid : null,
    };
  }

  /**
   * Execute a DevDocs operation through the GCP MCP integration
   * This is a helper method that can be used by the GCP MCP server to interact with DevDocs
   */
  async executeDevDocsOperation(operation: string, params: any): Promise<any> {
    try {
      switch (operation) {
        case 'listDocuments':
          return await devDocsService.listDocuments();

        case 'getDocument':
          if (!params.documentId) {
            throw new Error('Document ID is required');
          }
          return await devDocsService.getDocument(params.documentId);

        case 'uploadDocument':
          if (!params.file || !params.fileName || !params.contentType) {
            throw new Error('File, fileName, and contentType are required');
          }
          return await devDocsService.uploadDocument(
            params.file,
            params.fileName,
            params.contentType,
            params.documentType || DocumentType.OTHER
          );

        case 'deleteDocument':
          if (!params.documentId) {
            throw new Error('Document ID is required');
          }
          return await devDocsService.deleteDocument(params.documentId);

        case 'updateDocumentMetadata':
          if (!params.documentId || !params.updates) {
            throw new Error('Document ID and updates are required');
          }
          return await devDocsService.updateDocumentMetadata(params.documentId, params.updates);

        default:
          throw new Error(`Unknown operation: ${operation}`);
      }
    } catch (error) {
      console.error(`Error executing DevDocs operation ${operation}:`, error);
      throw error;
    }
  }
}

// Export a singleton instance of the service
export const gcpMcpIntegration = new GcpMcpIntegration();

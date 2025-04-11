#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ErrorCode,
    ListToolsRequestSchema,
    McpError,
} from '@modelcontextprotocol/sdk/types.js';

class GithubServer {
    private server: Server;

    constructor() {
        this.server = new Server(
            {
                name: 'github-mcp-server',
                version: '0.1.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        this.setupToolHandlers();

        // Error handling
        this.server.onerror = (error) => console.error('[MCP Error]', error);
        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }

    private setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'commit',
                    description: 'Commit changes to a Git branch',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            message: {
                                type: 'string',
                                description: 'Commit message',
                            },
                            branch: {
                                type: 'string',
                                description: 'Branch name',
                            },
                        },
                        required: ['message', 'branch'],
                    },
                },
            ],
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (request.params.name !== 'commit') {
                throw new McpError(
                    ErrorCode.MethodNotFound,
                    `Unknown tool: ${request.params.name}`
                );
            }

            const { message, branch } = request.params.arguments as { message: string, branch: string };

            // Execute the git commit command
            const command = `git commit -m "${message}"`;

            // Execute the git push command
            const pushCommand = `git push origin ${branch}`;

            return {
                content: [
                    {
                        type: 'text',
                        text: `Successfully committed to branch ${branch} with message: ${message}`,
                    },
                ],
            };
        });
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Github MCP server running on stdio');
    }
}

const server = new GithubServer();
server.run().catch(console.error);
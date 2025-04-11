"use client";

import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/i18n/LanguageProvider';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Play, Square, RefreshCw, Info } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface McpStatus {
  isRunning: boolean;
  processId: number | null;
}

const GcpMcpManager: React.FC = () => {
  const { t } = useLanguage();
  const [status, setStatus] = useState<McpStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch the status of the GCP MCP server
  const fetchStatus = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('/api/mcp');
      
      if (!response.ok) {
        throw new Error(`Failed to get MCP status: ${response.statusText}`);
      }
      
      const data = await response.json();
      setStatus(data.data);
    } catch (error) {
      console.error('Error fetching MCP status:', error);
      setError(error instanceof Error ? error.message : 'Failed to get MCP status');
    } finally {
      setIsLoading(false);
    }
  };

  // Start the GCP MCP server
  const startMcpServer = async () => {
    try {
      setIsStarting(true);
      setError(null);

      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'start' }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to start MCP server');
      }

      // Fetch the updated status
      await fetchStatus();
    } catch (error) {
      console.error('Error starting MCP server:', error);
      setError(error instanceof Error ? error.message : 'Failed to start MCP server');
    } finally {
      setIsStarting(false);
    }
  };

  // Stop the GCP MCP server
  const stopMcpServer = async () => {
    try {
      setIsStopping(true);
      setError(null);

      const response = await fetch('/api/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'stop' }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to stop MCP server');
      }

      // Fetch the updated status
      await fetchStatus();
    } catch (error) {
      console.error('Error stopping MCP server:', error);
      setError(error instanceof Error ? error.message : 'Failed to stop MCP server');
    } finally {
      setIsStopping(false);
    }
  };

  // Fetch the status on component mount
  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t('mcp.title')}</CardTitle>
        <CardDescription>{t('mcp.description')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertTitle>{t('common.error')}</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-medium">{t('mcp.status')}:</span>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : status?.isRunning ? (
              <Badge variant="success" className="bg-green-500">
                {t('mcp.running')}
              </Badge>
            ) : (
              <Badge variant="secondary" className="bg-gray-500">
                {t('mcp.stopped')}
              </Badge>
            )}
          </div>
          {status?.processId && (
            <div className="text-sm text-gray-500">
              PID: {status.processId}
            </div>
          )}
        </div>

        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>{t('mcp.info_title')}</AlertTitle>
          <AlertDescription>
            {t('mcp.info_description')}
          </AlertDescription>
        </Alert>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button
          variant="outline"
          onClick={fetchStatus}
          disabled={isLoading || isStarting || isStopping}
        >
          {isLoading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          {t('mcp.refresh')}
        </Button>
        <div className="space-x-2">
          <Button
            variant="outline"
            onClick={stopMcpServer}
            disabled={!status?.isRunning || isLoading || isStarting || isStopping}
          >
            {isStopping ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Square className="mr-2 h-4 w-4" />
            )}
            {t('mcp.stop')}
          </Button>
          <Button
            onClick={startMcpServer}
            disabled={status?.isRunning || isLoading || isStarting || isStopping}
          >
            {isStarting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Play className="mr-2 h-4 w-4" />
            )}
            {t('mcp.start')}
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
};

export default GcpMcpManager;

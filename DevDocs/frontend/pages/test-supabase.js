import { useState, useEffect } from 'react';
import getSupabaseClient from '../lib/supabaseClient';

export default function TestSupabasePage() {
  const [status, setStatus] = useState('Checking Supabase connection...');
  const [error, setError] = useState(null);
  const [connectionInfo, setConnectionInfo] = useState(null);

  useEffect(() => {
    async function testConnection() {
      try {
        const supabase = getSupabaseClient();
        
        if (!supabase) {
          setStatus('Failed: Supabase client not available');
          setError('Supabase client could not be initialized. Check your environment variables.');
          return;
        }

        // Test a simple query
        const { data, error } = await supabase
          .from('documents')
          .select('count')
          .limit(1);

        if (error) {
          setStatus('Failed: Error executing query');
          setError(error.message);
          return;
        }

        // Get connection info
        const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
        const keyPreview = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY 
          ? `${process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY.substring(0, 10)}...` 
          : 'Not available';

        setConnectionInfo({
          url,
          keyPreview,
        });

        setStatus('Success: Connected to Supabase');
      } catch (err) {
        setStatus('Failed: Exception occurred');
        setError(err.message);
      }
    }

    testConnection();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Supabase Connection Test</h1>
      
      <div className="mb-4 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-2">Status</h2>
        <p className={`font-medium ${status.startsWith('Success') ? 'text-green-600' : 'text-red-600'}`}>
          {status}
        </p>
        
        {error && (
          <div className="mt-2 p-2 bg-red-100 border border-red-300 rounded">
            <h3 className="font-semibold">Error Details:</h3>
            <p className="font-mono text-sm">{error}</p>
          </div>
        )}
      </div>

      {connectionInfo && (
        <div className="mb-4 p-4 border rounded">
          <h2 className="text-xl font-semibold mb-2">Connection Information</h2>
          <div className="grid grid-cols-2 gap-2">
            <div className="font-semibold">Supabase URL:</div>
            <div>{connectionInfo.url}</div>
            <div className="font-semibold">API Key (preview):</div>
            <div>{connectionInfo.keyPreview}</div>
          </div>
        </div>
      )}

      <div className="mt-4">
        <a href="/" className="text-blue-600 hover:underline">Back to Home</a>
      </div>
    </div>
  );
}

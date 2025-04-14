import React, { useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import FinDocLayout from '../components/FinDocLayout';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the dashboard page
    router.push('/dashboard');
  }, [router]);

  return (
    <FinDocLayout>
      <div className="welcome-container">
        <h1 className="welcome-title">FinDoc Financial Document Analysis</h1>

        <div className="welcome-card">
          <h2 className="welcome-subtitle">Welcome to FinDoc Analyzer</h2>
          <p className="welcome-text">
            This application helps financial professionals analyze documents, manage portfolios, and generate reports.
            You are being redirected to the dashboard...
          </p>

          <div className="welcome-buttons">
            <Link href="/dashboard">
              <button className="primary-button">Go to Dashboard</button>
            </Link>
            <Link href="/dev-test-center">
              <button className="secondary-button">Dev Testing Dashboard</button>
            </Link>
            <Link href="/test-center">
              <button className="secondary-button">Test Center</button>
            </Link>
            <Link href="/mcp-demo">
              <button className="secondary-button">MCP Demo</button>
            </Link>
          </div>
        </div>
      </div>

      <style jsx>{`
        .welcome-container {
          padding: 30px;
        }
        .welcome-title {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 20px;
          color: #2c3e50;
        }
        .welcome-card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          padding: 25px;
          margin-bottom: 30px;
        }
        .welcome-subtitle {
          font-size: 18px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
        }
        .welcome-text {
          color: #718096;
          margin-bottom: 20px;
          line-height: 1.6;
        }
        .welcome-buttons {
          display: flex;
          gap: 15px;
          margin-top: 20px;
        }
        .primary-button {
          background-color: #3498db;
          color: white;
          border: none;
          border-radius: 5px;
          padding: 10px 20px;
          font-size: 14px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        .primary-button:hover {
          background-color: #2980b9;
        }
        .secondary-button {
          background-color: #f1f5f9;
          color: #64748b;
          border: none;
          border-radius: 5px;
          padding: 10px 20px;
          font-size: 14px;
          cursor: pointer;
          transition: background-color 0.3s;
        }
        .secondary-button:hover {
          background-color: #e2e8f0;
        }
      `}</style>
    </FinDocLayout>
  );
}

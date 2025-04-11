import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function HomePage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Welcome to the Document Understanding Demo</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <Card>
          <CardHeader>
            <CardTitle>Document Upload Demo</CardTitle>
            <CardDescription>
              Upload and analyze financial documents with our AI-powered document understanding engine.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Our document understanding engine can extract key information from financial documents, including:
            </p>
            <ul className="list-disc pl-5 mb-6">
              <li>Financial metrics (revenue, profit, etc.)</li>
              <li>Company information</li>
              <li>Financial ratios</li>
              <li>Tabular data</li>
            </ul>
            <Link href="/document-demo">
              <Button className="w-full">Try Document Upload Demo</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Messos Financial Document Analysis</CardTitle>
            <CardDescription>
              See how our system analyzes a sample financial document from Messos Group.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              This demo shows a pre-loaded financial document from Messos Group and demonstrates how our system:
            </p>
            <ul className="list-disc pl-5 mb-6">
              <li>Identifies key financial metrics</li>
              <li>Calculates important financial ratios</li>
              <li>Extracts company information</li>
              <li>Provides a comprehensive analysis</li>
            </ul>
            <Link href="/messos-demo">
              <Button className="w-full">View Messos Demo</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>About Document Understanding</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">
            Our document understanding system uses advanced AI to automatically extract and analyze information from financial documents.
            This technology can save hours of manual data entry and analysis, while reducing errors and improving consistency.
          </p>
          
          <h3 className="text-lg font-semibold mt-6 mb-2">Key Features</h3>
          <ul className="list-disc pl-5 mb-6">
            <li>Automatic extraction of financial metrics and ratios</li>
            <li>Identification of company information and document metadata</li>
            <li>Table extraction and analysis</li>
            <li>Support for multiple document formats (PDF, Excel, CSV)</li>
            <li>Integration with existing financial systems</li>
          </ul>
          
          <h3 className="text-lg font-semibold mt-6 mb-2">Use Cases</h3>
          <ul className="list-disc pl-5">
            <li>Financial analysis and reporting</li>
            <li>Investment research</li>
            <li>Regulatory compliance</li>
            <li>Audit preparation</li>
            <li>Portfolio management</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"; // For displaying tables/ISINs

// Define structure for API responses (adjust based on actual data)
interface ExtractedTable {
  // Define table structure based on backend output
  // Example: Assuming list of lists for rows/cells
  rows: string[][];
  page_number?: number; // Optional page number
}

interface FinancialData {
  // Define structure based on backend output
  // Example: Assuming a list of ISINs
  isins?: { isin: string; description?: string; value?: string }[];
  entities?: { text: string; type: string }[]; // Other financial entities
  // Add other fields as needed
}

interface ApiDocument {
  document_id: string;
  filename: string | null;
  // Add other fields if needed from the /api/documents list endpoint
}

// --- Tab Content Components ---

const TableExtractionTab = ({ documentId }: { documentId: string | undefined }) => {
  const [tables, setTables] = useState<ExtractedTable[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    if (!documentId) {
      setTables([]);
      setError(null);
      setIsLoading(false);
      return;
    }

    const fetchTables = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/documents/${documentId}/tables`);
        if (!response.ok) {
          const errData = await response.json().catch(() => ({})); // Try to parse error
          throw new Error(errData.error || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setTables(data.tables || []); // Assuming the API returns { tables: [...] }
      } catch (err) {
        console.error("Failed to fetch tables:", err);
        setError(err instanceof Error ? err.message : "Could not fetch tables.");
        setTables([]);
         toast({ variant: "destructive", title: "Error Loading Tables", description: error });
      } finally {
        setIsLoading(false);
      }
    };

    fetchTables();
  }, [documentId, toast, error]); // Added error to dependency array

  return (
    <Card>
      <CardHeader>
        <CardTitle>Table Extraction</CardTitle>
        <CardDescription>View tables extracted from the selected document.</CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading && <p className="text-slate-500">Loading tables...</p>}
        {error && <p className="text-red-600">Error: {error}</p>}
        {!isLoading && !error && !documentId && <p className="text-slate-500">Select a document to view extracted tables.</p>}
        {!isLoading && !error && documentId && tables.length === 0 && <p className="text-slate-500">No tables found or extracted for this document.</p>}
        {!isLoading && !error && documentId && tables.length > 0 && (
          <div className="space-y-4">
            {tables.map((table, index) => (
              <div key={index} className="border rounded-lg overflow-hidden">
                 {table.page_number && <p className="text-xs text-slate-500 px-2 pt-1">Page: {table.page_number}</p>}
                 <Table>
                   <TableBody>
                     {table.rows.map((row, rowIndex) => (
                       <TableRow key={rowIndex}>
                         {row.map((cell, cellIndex) => (
                           <TableCell key={cellIndex} className="border px-2 py-1 text-sm">{cell}</TableCell>
                         ))}
                       </TableRow>
                     ))}
                   </TableBody>
                 </Table>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const ISINDetectionTab = ({ documentId }: { documentId: string | undefined }) => {
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

   useEffect(() => {
    if (!documentId) {
      setFinancialData(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    const fetchFinancialData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/documents/${documentId}/financial`);
         if (!response.ok) {
          // Handle specific status codes like 202 (Processing)
          if (response.status === 202) {
             setError("Financial data is still being processed.");
             setFinancialData(null);
             return; // Don't throw, just set error message
          }
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.error || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setFinancialData(data);
      } catch (err) {
        console.error("Failed to fetch financial data:", err);
        setError(err instanceof Error ? err.message : "Could not fetch financial data.");
        setFinancialData(null);
        toast({ variant: "destructive", title: "Error Loading Financial Data", description: error });
      } finally {
        setIsLoading(false);
      }
    };

    fetchFinancialData();
  }, [documentId, toast, error]); // Added error to dependency array

  const isins = financialData?.isins || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>ISIN Detection</CardTitle>
        <CardDescription>View detected ISINs and related information.</CardDescription>
      </CardHeader>
      <CardContent>
         {isLoading && <p className="text-slate-500">Loading financial data...</p>}
         {/* Display specific processing message */}
         {error && error === "Financial data is still being processed." && <p className="text-blue-600">{error}</p>}
         {/* Display other errors */}
         {error && error !== "Financial data is still being processed." && <p className="text-red-600">Error: {error}</p>}
         {!isLoading && !error && !documentId && <p className="text-slate-500">Select a document to view detected ISINs.</p>}
         {!isLoading && !error && documentId && isins.length === 0 && <p className="text-slate-500">No ISINs found or extracted for this document.</p>}
         {!isLoading && !error && documentId && isins.length > 0 && (
           <Table>
             <TableHeader>
               <TableRow>
                 <TableHead>ISIN</TableHead>
                 <TableHead>Description</TableHead>
                 <TableHead>Value</TableHead>
               </TableRow>
             </TableHeader>
             <TableBody>
               {isins.map((item, index) => (
                 <TableRow key={item.isin + index}>
                   <TableCell className="font-medium">{item.isin}</TableCell>
                   <TableCell>{item.description || 'N/A'}</TableCell>
                   <TableCell>{item.value || 'N/A'}</TableCell>
                 </TableRow>
               ))}
             </TableBody>
           </Table>
         )}
         {/* TODO: Display other financial entities if needed */}
      </CardContent>
    </Card>
  );
};


const DataVisualizationTab = ({ documentId }: { documentId: string | undefined }) => (
  // TODO: Implement fetching financial data and rendering charts
  <Card>
    <CardHeader>
      <CardTitle>Data Visualization</CardTitle>
      <CardDescription>Visualize financial data from the selected document.</CardDescription>
    </CardHeader>
    <CardContent>
      {!documentId && <p className="text-slate-500">Select a document to visualize data.</p>}
      {documentId && (
         <>
          <p className="text-slate-500">Visualization implementation needed.</p>
          <div className="mt-4 p-4 border rounded bg-slate-50 h-64">Chart Placeholder</div>
         </>
      )}
    </CardContent>
  </Card>
);

const CustomReportsTab = ({ documentId }: { documentId: string | undefined }) => (
 // TODO: Implement report generation form/options
  <Card>
    <CardHeader>
      <CardTitle>Custom Reports</CardTitle>
      <CardDescription>Generate tailored analysis reports.</CardDescription>
    </CardHeader>
    <CardContent>
       {!documentId && <p className="text-slate-500">Select a document to generate reports.</p>}
       {documentId && (
          <>
            <p className="text-slate-500">Report options implementation needed.</p>
            <div className="mt-4 p-4 border rounded bg-slate-50">Report Options Placeholder</div>
            <Button className="mt-4">Generate Report</Button>
          </>
       )}
    </CardContent>
  </Card>
);

// --- Main Page Component ---

export default function AnalysisPage() {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | undefined>(undefined);
  const [documents, setDocuments] = useState<ApiDocument[]>([]);
  const [isLoadingDocs, setIsLoadingDocs] = useState<boolean>(true);
  const { toast } = useToast();

  // Fetch document list for the dropdown
  useEffect(() => {
    const fetchDocList = async () => {
      setIsLoadingDocs(true);
      try {
        const response = await fetch('/api/documents');
        if (!response.ok) throw new Error("Failed to fetch document list");
        const data = await response.json();
        // Access the 'documents' array within the response object
        setDocuments(data.documents || []);
      } catch (error) {
        console.error("Failed to fetch document list:", error);
        toast({ variant: "destructive", title: "Error Loading Document List" });
        setDocuments([]);
      } finally {
        setIsLoadingDocs(false);
      }
    };
    fetchDocList();
  }, [toast]);


  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-slate-800">Analysis Tools</h1>
        {/* Document Selector */}
        <div className="w-[300px]">
           <Select
             value={selectedDocumentId}
             onValueChange={setSelectedDocumentId}
             disabled={isLoadingDocs || documents.length === 0}
            >
            <SelectTrigger>
              <SelectValue placeholder={isLoadingDocs ? "Loading documents..." : "Select a document..."} />
            </SelectTrigger>
            <SelectContent>
              {!isLoadingDocs && documents.length === 0 && <SelectItem value="no-docs" disabled>No documents available</SelectItem>}
              {documents.map(doc => (
                <SelectItem key={doc.document_id} value={doc.document_id}>{doc.filename || doc.document_id}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Tabs defaultValue="table-extraction" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="table-extraction">Table Extraction</TabsTrigger>
          <TabsTrigger value="isin-detection">ISIN Detection</TabsTrigger>
          <TabsTrigger value="visualization">Visualization</TabsTrigger>
          <TabsTrigger value="reports">Custom Reports</TabsTrigger>
        </TabsList>
        {/* Pass selectedDocumentId to each tab */}
        <TabsContent value="table-extraction">
          <TableExtractionTab documentId={selectedDocumentId} />
        </TabsContent>
        <TabsContent value="isin-detection">
          <ISINDetectionTab documentId={selectedDocumentId} />
        </TabsContent>
        <TabsContent value="visualization">
          <DataVisualizationTab documentId={selectedDocumentId} />
        </TabsContent>
        <TabsContent value="reports">
          <CustomReportsTab documentId={selectedDocumentId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
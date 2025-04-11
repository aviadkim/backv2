'use client'; // Needed for state and event handlers

import { useState, useEffect } from 'react'; // Added useEffect
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast"; // Import useToast for error handling

// Placeholder Icons
const MoreHorizontalIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /><circle cx="5" cy="12" r="1" /></svg>
);
const FilterIcon = ({ className }: { className?: string }) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" /></svg>
);
const SearchIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></svg>
);
const RefreshCwIcon = ({ className }: { className?: string }) => (
 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className || "h-4 w-4"}><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M3 21v-5h5"/></svg>
);


// Define the structure of the document data from the API
interface ApiDocument {
  document_id: string;
  filename: string | null;
  upload_date: string | null; // ISO string
  status: string | null;
  language: string | null;
  // Add other fields if available from API later (e.g., type, pages)
}

export default function DocumentsPage() {
  const [allDocuments, setAllDocuments] = useState<ApiDocument[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState('');
  // Removed filterType as it's not in API data yet
  const [filterStatus, setFilterStatus] = useState('all');
  const { toast } = useToast();

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/documents'); // Fetch from the backend endpoint
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Access the 'documents' array within the response object
      setAllDocuments(data.documents || []);
    } catch (error) {
      console.error("Failed to fetch documents:", error);
      toast({
        variant: "destructive",
        title: "Failed to Load Documents",
        description: error instanceof Error ? error.message : "Could not fetch document list from the server.",
      });
      setAllDocuments([]); // Clear documents on error
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch documents when the component mounts
  useEffect(() => {
    fetchDocuments();
  }, []);

  // Basic filtering logic (adjust based on available data)
  const filteredDocuments = allDocuments.filter(doc =>
    (doc.filename?.toLowerCase() || '').includes(searchTerm.toLowerCase()) &&
    (filterStatus === 'all' || doc.status === filterStatus)
  );

  const getStatusBadgeVariant = (status: string | null): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case "Processed": return "default";
      case "Processing": return "secondary";
      case "Error": return "destructive";
      default: return "outline";
    }
  };

  // Format date for display
  const formatDate = (isoString: string | null): string => {
    if (!isoString) return 'N/A';
    try {
      return new Date(isoString).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
      });
    } catch {
      return 'Invalid Date';
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex justify-between items-center">
         <h1 className="text-2xl font-semibold text-slate-800">My Documents</h1>
         <Button variant="outline" size="sm" onClick={fetchDocuments} disabled={isLoading}>
            <RefreshCwIcon className={`mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
         </Button>
      </div>


      <Card>
        <CardHeader>
          <CardTitle>Document Library</CardTitle>
          <CardDescription>Search, filter, and manage your uploaded documents.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filter and Search Controls */}
          <div className="flex flex-col md:flex-row items-center gap-4 mb-6">
            <div className="relative flex-1 w-full md:w-auto md:grow">
              <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
              <Input
                type="search"
                placeholder="Search by filename..."
                className="pl-8 w-full"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="flex gap-2 w-full md:w-auto">
               {/* Removed Type filter for now */}
               <Select value={filterStatus} onValueChange={setFilterStatus} disabled={isLoading}>
                <SelectTrigger className="w-full md:w-[160px]">
                  <SelectValue placeholder="Filter by Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="Processed">Processed</SelectItem>
                  <SelectItem value="Processing">Processing</SelectItem>
                  <SelectItem value="Error">Error</SelectItem>
                  {/* Add other statuses if needed */}
                </SelectContent>
              </Select>
              {/* Filter button might be less useful without more filters */}
              {/* <Button variant="outline" className="hidden md:inline-flex">
                <FilterIcon className="mr-2 h-4 w-4" /> Filter
              </Button> */}
            </div>
          </div>

          {/* Documents Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Filename</TableHead>
                  <TableHead>Upload Date</TableHead>
                  {/* Removed Type and Pages */}
                  <TableHead>Language</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                   <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center text-slate-500">
                      Loading documents...
                    </TableCell>
                  </TableRow>
                ) : filteredDocuments.length > 0 ? (
                  filteredDocuments.map((doc) => (
                    <TableRow key={doc.document_id}>
                      <TableCell className="font-medium text-slate-800">{doc.filename || 'N/A'}</TableCell>
                      <TableCell className="text-slate-600">{formatDate(doc.upload_date)}</TableCell>
                      <TableCell className="text-slate-600">{doc.language || 'N/A'}</TableCell>
                      <TableCell>
                        <Badge variant={getStatusBadgeVariant(doc.status)}>{doc.status || 'Unknown'}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontalIcon />
                              <span className="sr-only">Actions</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {/* TODO: Link actions to actual functionality */}
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Analyze</DropdownMenuItem>
                            <DropdownMenuItem>Download Results</DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem>Share</DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} className="h-24 text-center text-slate-500">
                      No documents found matching your criteria.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>

           {/* TODO: Add Pagination if API supports it */}

        </CardContent>
      </Card>
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import { useLanguage } from '@/i18n/LanguageProvider';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Loader2, Upload, FileText, Trash2, Download, Eye, Tag, Edit, Check, X } from "lucide-react";
import { DocumentType } from '@/services/devDocs';
import { format } from 'date-fns';

// Document metadata interface
interface DocumentMetadata {
  id: string;
  name: string;
  type: DocumentType;
  uploadedAt: string;
  size: number;
  mimeType: string;
  url: string;
  tags?: string[];
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  processingResult?: any;
}

const DevDocsManager: React.FC = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('upload');
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType>(DocumentType.FINANCIAL_STATEMENT);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingError, setLoadingError] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<DocumentMetadata | null>(null);
  const [newTag, setNewTag] = useState('');
  const [isAddingTag, setIsAddingTag] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Load documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);

  // Load documents from the API
  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      setLoadingError(null);

      const response = await fetch('/api/devdocs');
      
      if (!response.ok) {
        throw new Error(`Failed to load documents: ${response.statusText}`);
      }
      
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Error loading documents:', error);
      setLoadingError(error instanceof Error ? error.message : 'Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle file change
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUploadError(null);
    }
  };

  // Handle document type change
  const handleDocumentTypeChange = (value: string) => {
    setDocumentType(value as DocumentType);
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      setUploadError('Please select a file to upload');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('documentType', documentType);

      const response = await fetch('/api/devdocs', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload document');
      }

      // Reset form
      setFile(null);
      if (document.getElementById('file-upload') instanceof HTMLInputElement) {
        (document.getElementById('file-upload') as HTMLInputElement).value = '';
      }

      // Reload documents
      await loadDocuments();

      // Switch to the documents tab
      setActiveTab('documents');
    } catch (error) {
      console.error('Error uploading document:', error);
      setUploadError(error instanceof Error ? error.message : 'Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle document selection
  const handleSelectDocument = (document: DocumentMetadata) => {
    setSelectedDocument(document);
    setActiveTab('view');
  };

  // Handle document download
  const handleDownload = async () => {
    if (!selectedDocument) return;

    try {
      window.open(`/api/devdocs?id=${selectedDocument.id}&content=true`, '_blank');
    } catch (error) {
      console.error('Error downloading document:', error);
    }
  };

  // Handle document deletion
  const handleDelete = async () => {
    if (!selectedDocument) return;

    try {
      setIsDeleting(true);

      const response = await fetch(`/api/devdocs?id=${selectedDocument.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to delete document');
      }

      // Reload documents
      await loadDocuments();

      // Reset selected document
      setSelectedDocument(null);

      // Switch to the documents tab
      setActiveTab('documents');
    } catch (error) {
      console.error('Error deleting document:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  // Handle adding a tag
  const handleAddTag = async () => {
    if (!selectedDocument || !newTag.trim()) return;

    try {
      setIsAddingTag(true);

      // Get current tags or initialize empty array
      const currentTags = selectedDocument.tags || [];
      
      // Add new tag if it doesn't already exist
      if (!currentTags.includes(newTag.trim())) {
        const updatedTags = [...currentTags, newTag.trim()];
        
        const response = await fetch(`/api/devdocs?id=${selectedDocument.id}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ tags: updatedTags }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to add tag');
        }

        const data = await response.json();
        
        // Update selected document
        setSelectedDocument(data.metadata);
        
        // Update document in the list
        setDocuments(documents.map(doc => 
          doc.id === selectedDocument.id ? data.metadata : doc
        ));
      }

      // Reset new tag input
      setNewTag('');
    } catch (error) {
      console.error('Error adding tag:', error);
    } finally {
      setIsAddingTag(false);
    }
  };

  // Handle removing a tag
  const handleRemoveTag = async (tagToRemove: string) => {
    if (!selectedDocument) return;

    try {
      // Get current tags
      const currentTags = selectedDocument.tags || [];
      
      // Remove the tag
      const updatedTags = currentTags.filter(tag => tag !== tagToRemove);
      
      const response = await fetch(`/api/devdocs?id=${selectedDocument.id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tags: updatedTags }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to remove tag');
      }

      const data = await response.json();
      
      // Update selected document
      setSelectedDocument(data.metadata);
      
      // Update document in the list
      setDocuments(documents.map(doc => 
        doc.id === selectedDocument.id ? data.metadata : doc
      ));
    } catch (error) {
      console.error('Error removing tag:', error);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Get status badge color
  const getStatusBadgeColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'processing':
        return 'bg-blue-500';
      case 'pending':
        return 'bg-yellow-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">{t('devdocs.upload')}</TabsTrigger>
          <TabsTrigger value="documents">{t('devdocs.documents')}</TabsTrigger>
          <TabsTrigger value="view" disabled={!selectedDocument}>{t('devdocs.view')}</TabsTrigger>
        </TabsList>
        
        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('devdocs.upload_document')}</CardTitle>
              <CardDescription>{t('devdocs.upload_description')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="file-upload">{t('devdocs.file')}</Label>
                <Input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="document-type">{t('devdocs.document_type')}</Label>
                <Select
                  value={documentType}
                  onValueChange={handleDocumentTypeChange}
                  disabled={isUploading}
                >
                  <SelectTrigger id="document-type">
                    <SelectValue placeholder={t('devdocs.select_document_type')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={DocumentType.FINANCIAL_STATEMENT}>{t('devdocs.financial_statement')}</SelectItem>
                    <SelectItem value={DocumentType.PORTFOLIO_STATEMENT}>{t('devdocs.portfolio_statement')}</SelectItem>
                    <SelectItem value={DocumentType.ANNUAL_REPORT}>{t('devdocs.annual_report')}</SelectItem>
                    <SelectItem value={DocumentType.TAX_DOCUMENT}>{t('devdocs.tax_document')}</SelectItem>
                    <SelectItem value={DocumentType.INVOICE}>{t('devdocs.invoice')}</SelectItem>
                    <SelectItem value={DocumentType.RECEIPT}>{t('devdocs.receipt')}</SelectItem>
                    <SelectItem value={DocumentType.OTHER}>{t('devdocs.other')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {uploadError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                  {uploadError}
                </div>
              )}
              
              {file && (
                <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded relative">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-sm">{formatFileSize(file.size)}</p>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button
                onClick={handleUpload}
                disabled={!file || isUploading}
                className="w-full"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {t('devdocs.uploading')}
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    {t('devdocs.upload')}
                  </>
                )}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('devdocs.documents')}</CardTitle>
              <CardDescription>{t('devdocs.documents_description')}</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center items-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : loadingError ? (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                  {loadingError}
                </div>
              ) : documents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p>{t('devdocs.no_documents')}</p>
                  <Button
                    variant="link"
                    onClick={() => setActiveTab('upload')}
                    className="mt-2"
                  >
                    {t('devdocs.upload_first_document')}
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableCaption>{t('devdocs.documents_list')}</TableCaption>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('devdocs.name')}</TableHead>
                      <TableHead>{t('devdocs.type')}</TableHead>
                      <TableHead>{t('devdocs.uploaded_at')}</TableHead>
                      <TableHead>{t('devdocs.size')}</TableHead>
                      <TableHead>{t('devdocs.status')}</TableHead>
                      <TableHead className="text-right">{t('devdocs.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {documents.map((document) => (
                      <TableRow key={document.id}>
                        <TableCell className="font-medium">{document.name}</TableCell>
                        <TableCell>{t(`devdocs.${document.type}`)}</TableCell>
                        <TableCell>{format(new Date(document.uploadedAt), 'PPP')}</TableCell>
                        <TableCell>{formatFileSize(document.size)}</TableCell>
                        <TableCell>
                          <Badge className={getStatusBadgeColor(document.processingStatus)}>
                            {t(`devdocs.${document.processingStatus}`)}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSelectDocument(document)}
                          >
                            <Eye className="h-4 w-4" />
                            <span className="sr-only">{t('devdocs.view')}</span>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                variant="outline"
                onClick={() => loadDocuments()}
                disabled={isLoading}
              >
                {t('devdocs.refresh')}
              </Button>
              <Button
                onClick={() => setActiveTab('upload')}
              >
                <Upload className="mr-2 h-4 w-4" />
                {t('devdocs.upload_new')}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        {/* View Tab */}
        <TabsContent value="view" className="space-y-4">
          {selectedDocument && (
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle>{selectedDocument.name}</CardTitle>
                    <CardDescription>
                      {t(`devdocs.${selectedDocument.type}`)} • {formatFileSize(selectedDocument.size)} • {format(new Date(selectedDocument.uploadedAt), 'PPP')}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusBadgeColor(selectedDocument.processingStatus)}>
                    {t(`devdocs.${selectedDocument.processingStatus}`)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Tags */}
                <div className="space-y-2">
                  <Label>{t('devdocs.tags')}</Label>
                  <div className="flex flex-wrap gap-2">
                    {selectedDocument.tags && selectedDocument.tags.length > 0 ? (
                      selectedDocument.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                          {tag}
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-4 w-4 p-0"
                            onClick={() => handleRemoveTag(tag)}
                          >
                            <X className="h-3 w-3" />
                            <span className="sr-only">{t('devdocs.remove_tag')}</span>
                          </Button>
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">{t('devdocs.no_tags')}</span>
                    )}
                  </div>
                  <div className="flex mt-2">
                    <Input
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder={t('devdocs.add_tag')}
                      className="mr-2"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleAddTag}
                      disabled={!newTag.trim() || isAddingTag}
                    >
                      {isAddingTag ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Tag className="h-4 w-4 mr-1" />
                      )}
                      {t('devdocs.add')}
                    </Button>
                  </div>
                </div>
                
                {/* Document Preview */}
                <div className="space-y-2">
                  <Label>{t('devdocs.preview')}</Label>
                  <div className="border rounded-md p-4 h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-900">
                    <div className="text-center">
                      <FileText className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-sm text-gray-500">{t('devdocs.preview_not_available')}</p>
                      <Button
                        variant="link"
                        size="sm"
                        onClick={handleDownload}
                      >
                        {t('devdocs.download_to_view')}
                      </Button>
                    </div>
                  </div>
                </div>
                
                {/* Processing Results */}
                {selectedDocument.processingStatus === 'completed' && selectedDocument.processingResult && (
                  <div className="space-y-2">
                    <Label>{t('devdocs.processing_results')}</Label>
                    <div className="border rounded-md p-4 max-h-64 overflow-auto bg-gray-50 dark:bg-gray-900">
                      <pre className="text-xs whitespace-pre-wrap">
                        {JSON.stringify(selectedDocument.processingResult, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button
                  variant="destructive"
                  onClick={handleDelete}
                  disabled={isDeleting}
                >
                  {isDeleting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Trash2 className="mr-2 h-4 w-4" />
                  )}
                  {t('devdocs.delete')}
                </Button>
                <div className="space-x-2">
                  <Button
                    variant="outline"
                    onClick={() => setActiveTab('documents')}
                  >
                    {t('devdocs.back_to_list')}
                  </Button>
                  <Button
                    onClick={handleDownload}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    {t('devdocs.download')}
                  </Button>
                </div>
              </CardFooter>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DevDocsManager;

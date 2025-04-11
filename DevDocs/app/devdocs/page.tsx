"use client";

import React, { useState } from 'react';
import { useLanguage } from '@/i18n/LanguageProvider';
import DevDocsManager from '@/components/DevDocsManager';
import GcpMcpManager from '@/components/GcpMcpManager';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function DevDocsPage() {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('documents');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('devdocs.title')}</h1>
        <p className="text-muted-foreground">
          {t('devdocs.description')}
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="documents">{t('devdocs.documents')}</TabsTrigger>
          <TabsTrigger value="mcp">{t('mcp.title')}</TabsTrigger>
        </TabsList>

        <TabsContent value="documents" className="space-y-4">
          <DevDocsManager />
        </TabsContent>

        <TabsContent value="mcp" className="space-y-4">
          <GcpMcpManager />
        </TabsContent>
      </Tabs>
    </div>
  );
}

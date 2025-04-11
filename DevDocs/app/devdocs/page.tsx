"use client";

import React from 'react';
import { useLanguage } from '@/i18n/LanguageProvider';
import DevDocsManager from '@/components/DevDocsManager';

export default function DevDocsPage() {
  const { t } = useLanguage();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('devdocs.title')}</h1>
        <p className="text-muted-foreground">
          {t('devdocs.description')}
        </p>
      </div>
      <DevDocsManager />
    </div>
  );
}

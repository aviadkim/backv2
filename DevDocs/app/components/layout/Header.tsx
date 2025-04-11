import React from 'react';
import { ModeToggle } from '@/components/ui/mode-toggle';
import { Button } from '@/components/ui/button';
import { Bell, Search, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import LanguageSelector from '@/components/LanguageSelector';
import { useLanguage } from '@/i18n/LanguageProvider';

const Header: React.FC = () => {
  const { t } = useLanguage();

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-6">
      <div className="flex flex-1 items-center gap-4 md:gap-6">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder={t('common.search')}
            className="w-full bg-background pl-8 md:w-[300px] lg:w-[400px]"
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <LanguageSelector variant="minimal" />
        <ModeToggle />
        <Button variant="ghost" size="icon" className="rounded-full">
          <Bell className="h-5 w-5" />
          <span className="sr-only">{t('common.notifications')}</span>
        </Button>
        <Button variant="ghost" size="icon" className="rounded-full">
          <User className="h-5 w-5" />
          <span className="sr-only">{t('common.profile')}</span>
        </Button>
      </div>
    </header>
  );
};

export default Header;

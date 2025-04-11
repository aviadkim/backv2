import React from 'react';
import { useLanguage } from '@/i18n/LanguageProvider';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Globe } from 'lucide-react';

interface LanguageSelectorProps {
  variant?: 'default' | 'minimal';
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ variant = 'default' }) => {
  const { language, setLanguage, availableLanguages } = useLanguage();

  const handleLanguageChange = (value: string) => {
    setLanguage(value);
  };

  if (variant === 'minimal') {
    return (
      <Select value={language} onValueChange={handleLanguageChange}>
        <SelectTrigger className="w-[70px]">
          <SelectValue placeholder={language.toUpperCase()} />
        </SelectTrigger>
        <SelectContent>
          {Object.entries(availableLanguages).map(([code, name]) => (
            <SelectItem key={code} value={code}>
              {code.toUpperCase()}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  }

  return (
    <Select value={language} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-[180px]">
        <Globe className="mr-2 h-4 w-4" />
        <SelectValue placeholder={availableLanguages[language]} />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(availableLanguages).map(([code, name]) => (
          <SelectItem key={code} value={code}>
            {name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export default LanguageSelector;

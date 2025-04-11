import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

// Import language files
import en from './locales/en.json';
import he from './locales/he.json';

// Define available languages
const languages = {
  en,
  he
};

type LanguageContextType = {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string) => string;
  availableLanguages: { [key: string]: string };
};

// Create context
const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  t: () => '',
  availableLanguages: { en: 'English', he: 'עברית' }
});

// Language provider props
interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  // Get initial language from localStorage or use browser language or default to English
  const getBrowserLanguage = () => {
    const browserLang = navigator.language.split('-')[0];
    return Object.keys(languages).includes(browserLang) ? browserLang : 'en';
  };

  const [language, setLanguageState] = useState<string>(
    typeof window !== 'undefined'
      ? localStorage.getItem('language') || getBrowserLanguage()
      : 'en'
  );

  // Available languages for UI
  const availableLanguages = {
    en: 'English',
    he: 'עברית'
  };

  // Update language and save to localStorage
  const setLanguage = (lang: string) => {
    if (Object.keys(languages).includes(lang)) {
      setLanguageState(lang);
      if (typeof window !== 'undefined') {
        localStorage.setItem('language', lang);
      }
      // Update HTML lang attribute
      document.documentElement.lang = lang;
    }
  };

  // Translation function
  const t = (key: string): string => {
    // Split the key by dots to access nested properties
    const keys = key.split('.');

    // Get the current language object
    const langObj = languages[language as keyof typeof languages] || languages.en;

    // Navigate through the object using the keys
    let result: any = langObj;
    for (const k of keys) {
      result = result?.[k];
      if (result === undefined) break;
    }

    // If translation not found, try English as fallback
    if (result === undefined && language !== 'en') {
      result = languages.en;
      for (const k of keys) {
        result = result?.[k];
        if (result === undefined) break;
      }
    }

    // If still not found, return the key itself
    return result || key;
  };

  // Set HTML lang attribute on mount and language change
  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, availableLanguages }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Custom hook to use the language context
export const useLanguage = () => useContext(LanguageContext);

// Export default for convenience
export default LanguageProvider;

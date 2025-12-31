import { useContext, createContext, useState, ReactNode } from 'react';
import { translations, Language, TranslationKey } from './translations';

interface TranslationContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: TranslationKey) => string;
}

const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

export function TranslationProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    // Récupérer la langue sauvegardée ou détecter depuis le navigateur
    const saved = localStorage.getItem('alignTester_language');
    if (saved === 'fr' || saved === 'en') {
      return saved;
    }
    // Détecter la langue du navigateur
    const browserLang = navigator.language.split('-')[0];
    return browserLang === 'fr' ? 'fr' : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('alignTester_language', lang);
  };

  const t = (key: TranslationKey): string => {
    return translations[language][key] || key;
  };

  return (
    <TranslationContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error('useTranslation must be used within TranslationProvider');
  }
  return context;
}


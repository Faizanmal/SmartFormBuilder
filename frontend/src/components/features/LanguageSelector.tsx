'use client';

import { useState, useEffect } from 'react';
import { i18nAPI } from '@/lib/advancedFeaturesAPI';
import { Language, FormTranslation } from '@/types/advancedFeatures';

interface LanguageSelectorProps {
  formId: string;
  currentLanguage?: string;
  onLanguageChange: (language: string) => void;
}

export default function LanguageSelector({ formId, currentLanguage, onLanguageChange }: LanguageSelectorProps) {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [translations, setTranslations] = useState<FormTranslation[]>([]);
  const [loading, setLoading] = useState(true);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    loadLanguages();
    loadTranslations();
  }, [formId]);

  const loadLanguages = async () => {
    try {
      const data = await i18nAPI.getLanguages();
      setLanguages(data);
    } catch (error) {
      console.error('Failed to load languages:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadTranslations = async () => {
    try {
      const data = await i18nAPI.getFormTranslations(formId);
      setTranslations(data);
    } catch (error) {
      console.error('Failed to load translations:', error);
    }
  };

  const handleAutoTranslate = async (targetLang: string) => {
    setTranslating(true);
    try {
      await i18nAPI.autoTranslateForm(formId, targetLang);
      await loadTranslations();
      onLanguageChange(targetLang);
    } catch (error) {
      console.error('Auto-translate failed:', error);
      alert('Translation failed. Please try again.');
    } finally {
      setTranslating(false);
    }
  };

  if (loading) {
    return <div className="animate-pulse">Loading languages...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Language Settings</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Language
          </label>
          <select
            value={currentLanguage || ''}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
          >
            {languages.map((lang) => (
              <option key={lang.id} value={lang.code}>
                {lang.native_name} ({lang.name})
              </option>
            ))}
          </select>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Available Translations</h4>
          <div className="space-y-2">
            {translations.map((translation) => (
              <div key={translation.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{translation.language_name}</span>
                  {translation.auto_translated && (
                    <span className="ml-2 text-xs text-orange-600">Auto-translated</span>
                  )}
                  {translation.verified_by_human && (
                    <span className="ml-2 text-xs text-green-600">✓ Verified</span>
                  )}
                </div>
                <button
                  onClick={() => onLanguageChange(translation.language_code || '')}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Use
                </button>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Quick Translate</h4>
          <div className="flex flex-wrap gap-2">
            {languages
              .filter((lang) => !translations.find((t) => t.language_code === lang.code))
              .map((lang) => (
                <button
                  key={lang.id}
                  onClick={() => handleAutoTranslate(lang.code)}
                  disabled={translating}
                  className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  + {lang.name}
                </button>
              ))}
          </div>
          {translating && (
            <p className="text-sm text-gray-600 mt-2">Translating with AI...</p>
          )}
        </div>
      </div>
    </div>
  );
}

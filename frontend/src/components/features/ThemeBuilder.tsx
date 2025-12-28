'use client';

import { useState, useEffect } from 'react';
import { themeAPI } from '@/lib/advancedFeaturesAPI';
import { Theme, ThemeColors, ThemeTypography } from '@/types/advancedFeatures';

interface ThemeBuilderProps {
  formId?: string;
  onSave?: (theme: Theme) => void;
}

export default function ThemeBuilder({ formId, onSave }: ThemeBuilderProps) {
  const [themes, setThemes] = useState<Theme[]>([]);
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);

  const [colors, setColors] = useState<ThemeColors>({
    primary: '#3B82F6',
    secondary: '#8B5CF6',
    accent: '#10B981',
    background: '#FFFFFF',
    surface: '#F3F4F6',
    error: '#EF4444',
    success: '#10B981',
    warning: '#F59E0B',
    text_primary: '#111827',
    text_secondary: '#6B7280',
  });

  const [typography, setTypography] = useState<ThemeTypography>({
    font_family: 'Inter, sans-serif',
    font_size_base: 16,
    font_size_heading: 24,
    font_weight_normal: 400,
    font_weight_bold: 700,
    line_height: 1.5,
  });

  const [customCSS, setCustomCSS] = useState('');

  useEffect(() => {
    loadThemes();
  }, []);

  const loadThemes = async () => {
    setLoading(true);
    try {
      const data = await themeAPI.getThemes();
      setThemes(data);
    } catch (error) {
      console.error('Failed to load themes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleColorChange = (key: keyof ThemeColors, value: string) => {
    setColors((prev) => ({ ...prev, [key]: value }));
  };

  const handleTypographyChange = (key: keyof ThemeTypography, value: string | number) => {
    setTypography((prev) => ({ ...prev, [key]: value }));
  };

  const handleSaveTheme = async () => {
    setLoading(true);
    try {
      const themeData = {
        name: selectedTheme?.name || 'Custom Theme',
        description: 'Custom theme',
        colors,
        typography,
        spacing: { unit: 8, padding: {}, margin: {} },
        borders: {},
        shadows: {},
        custom_css: customCSS,
        is_public: false,
      };

      const newTheme = selectedTheme?.id
        ? await themeAPI.updateTheme(selectedTheme.id, themeData)
        : await themeAPI.createTheme(themeData);

      setSelectedTheme(newTheme);
      if (onSave) onSave(newTheme);
      await loadThemes();
      setIsEditing(false);
      alert('Theme saved successfully!');
    } catch (error) {
      console.error('Failed to save theme:', error);
      alert('Failed to save theme');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectTheme = async (theme: Theme) => {
    setSelectedTheme(theme);
    setColors(theme.colors);
    setTypography(theme.typography);
    setCustomCSS(theme.custom_css || '');
    setIsEditing(false);
  };

  const handleCloneTheme = async (themeId: string) => {
    try {
      const clonedTheme = await themeAPI.cloneTheme(themeId);
      await loadThemes();
      setSelectedTheme(clonedTheme);
      alert('Theme cloned successfully!');
    } catch (error) {
      console.error('Failed to clone theme:', error);
      alert('Failed to clone theme');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <h2 className="text-2xl font-bold">Theme Builder</h2>
        <p className="text-gray-600 mt-1">Customize your form&apos;s appearance</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Theme List */}
        <div className="lg:col-span-1">
          <h3 className="font-semibold mb-4">Available Themes</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {themes.map((theme) => (
              <div
                key={theme.id}
                className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                  selectedTheme?.id === theme.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => handleSelectTheme(theme)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">{theme.name}</div>
                    <div className="text-xs text-gray-500">
                      {theme.is_public ? 'Public' : 'Private'}
                    </div>
                  </div>
                  <div className="flex gap-1">
                    {Object.values(theme.colors).slice(0, 3).map((color, idx) => (
                      <div
                        key={idx}
                        className="w-6 h-6 rounded"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>
                {theme.rating_count > 0 && (
                  <div className="text-xs text-yellow-600 mt-1">
                    ★ {theme.rating_average.toFixed(1)} ({theme.rating_count} ratings)
                  </div>
                )}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleCloneTheme(theme.id);
                  }}
                  className="text-xs text-blue-600 hover:underline mt-2"
                >
                  Clone
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={() => {
              setSelectedTheme(null);
              setIsEditing(true);
            }}
            className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Create New Theme
          </button>
        </div>

        {/* Theme Editor */}
        <div className="lg:col-span-2">
          {selectedTheme || isEditing ? (
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-4">Colors</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(colors).map(([key, value]) => (
                    <div key={key}>
                      <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                        {key.replace(/_/g, ' ')}
                      </label>
                      <div className="flex gap-2">
                        <input
                          type="color"
                          value={value}
                          onChange={(e) => handleColorChange(key as keyof ThemeColors, e.target.value)}
                          className="w-12 h-10 border rounded cursor-pointer"
                        />
                        <input
                          type="text"
                          value={value}
                          onChange={(e) => handleColorChange(key as keyof ThemeColors, e.target.value)}
                          className="flex-1 px-3 py-2 border rounded"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-4">Typography</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Font Family
                    </label>
                    <input
                      type="text"
                      value={typography.font_family}
                      onChange={(e) => handleTypographyChange('font_family', e.target.value)}
                      className="w-full px-3 py-2 border rounded"
                      placeholder="Inter, sans-serif"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Base Font Size
                    </label>
                    <input
                      type="number"
                      value={typography.font_size_base}
                      onChange={(e) => handleTypographyChange('font_size_base', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Heading Font Size
                    </label>
                    <input
                      type="number"
                      value={typography.font_size_heading}
                      onChange={(e) => handleTypographyChange('font_size_heading', parseInt(e.target.value))}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-4">Custom CSS</h3>
                <textarea
                  value={customCSS}
                  onChange={(e) => setCustomCSS(e.target.value)}
                  className="w-full h-32 px-3 py-2 border rounded font-mono text-sm"
                  placeholder="/* Add custom CSS here */"
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSaveTheme}
                  disabled={loading}
                  className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Saving...' : 'Save Theme'}
                </button>
                <button
                  onClick={() => {
                    setSelectedTheme(null);
                    setIsEditing(false);
                  }}
                  className="px-6 py-2 border border-gray-300 rounded hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-12">
              Select a theme to edit or create a new one
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Contrast, Pause, Play, Keyboard, MousePointer, Eye, CheckCircle, AlertCircle } from 'lucide-react';
import { 
  setupReducedMotionListener, 
  runA11yAudit,
  announceToScreenReader,
  prefersReducedMotion,
  prefersHighContrast,
} from '@/lib/accessibility';

export function AccessibilitySettings() {
  const loadPreferences = () => {
    const saved = localStorage.getItem('a11yPreferences');
    return saved ? JSON.parse(saved) : {};
  };

  const prefs = loadPreferences();
  const [reducedMotion, setReducedMotion] = useState(prefs.reducedMotion || prefersReducedMotion());
  const [highContrast, setHighContrast] = useState(prefs.highContrast || prefersHighContrast());
  const [fontSize, setFontSize] = useState(prefs.fontSize || 16);
  const [keyboardNav, setKeyboardNav] = useState(prefs.keyboardNav !== false);
  const [focusIndicator, setFocusIndicator] = useState(prefs.focusIndicator !== false);
  const [auditResults, setAuditResults] = useState<{ valid: boolean; issues: Array<{ category: string; issues: string[] }> } | null>(null);

  const savePreferences = (prefs: Record<string, unknown>) => {
    localStorage.setItem('a11yPreferences', JSON.stringify(prefs));
  };

  const applyAccessibilitySettings = (prefs: Record<string, unknown>) => {
    const root = document.documentElement;

    // Font size
    if (prefs.fontSize) {
      root.style.fontSize = `${prefs.fontSize}px`;
    }

    // Motion
    if (prefs.reducedMotion) {
      root.style.setProperty('--motion-reduce', '1');
    }

    // High contrast
    if (prefs.highContrast) {
      root.classList.add('high-contrast');
    }

    // Focus indicators
    if (!prefs.focusIndicator) {
      root.classList.add('no-focus-indicator');
    }
  };

  const applyMotionPreference = (reduced: boolean) => {
    const root = document.documentElement;
    if (reduced) {
      root.style.setProperty('--motion-reduce', '1');
    } else {
      root.style.removeProperty('--motion-reduce');
    }
  };

  useEffect(() => {
    // Load preferences from localStorage
    const prefs = loadPreferences();
    setReducedMotion(prefs.reducedMotion || prefersReducedMotion());
    setHighContrast(prefs.highContrast || prefersHighContrast());
    setFontSize(prefs.fontSize || 16);
    setKeyboardNav(prefs.keyboardNav !== false);
    setFocusIndicator(prefs.focusIndicator !== false);

    // Apply settings
    applyAccessibilitySettings(prefs);

    // Listen for system preference changes
    const cleanup = setupReducedMotionListener((reduced) => {
      if (!prefs.reducedMotion) { // Only if not manually set
        setReducedMotion(reduced);
        applyMotionPreference(reduced);
      }
    });

    return cleanup;
  }, []);

  const handleReducedMotionToggle = (enabled: boolean) => {
    setReducedMotion(enabled);
    const prefs = { ...loadPreferences(), reducedMotion: enabled };
    savePreferences(prefs);
    applyMotionPreference(enabled);
    announceToScreenReader(
      enabled ? 'Reduced motion enabled' : 'Animations enabled'
    );
  };

  const handleHighContrastToggle = (enabled: boolean) => {
    setHighContrast(enabled);
    const prefs = { ...loadPreferences(), highContrast: enabled };
    savePreferences(prefs);
    
    const root = document.documentElement;
    if (enabled) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }
    
    announceToScreenReader(
      enabled ? 'High contrast mode enabled' : 'High contrast mode disabled'
    );
  };

  const handleFontSizeChange = (value: number[]) => {
    const size = value[0];
    setFontSize(size);
    const prefs = { ...loadPreferences(), fontSize: size };
    savePreferences(prefs);
    document.documentElement.style.fontSize = `${size}px`;
    announceToScreenReader(`Font size set to ${size} pixels`);
  };

  const handleKeyboardNavToggle = (enabled: boolean) => {
    setKeyboardNav(enabled);
    const prefs = { ...loadPreferences(), keyboardNav: enabled };
    savePreferences(prefs);
    announceToScreenReader(
      enabled ? 'Keyboard navigation enabled' : 'Keyboard navigation disabled'
    );
  };

  const handleFocusIndicatorToggle = (enabled: boolean) => {
    setFocusIndicator(enabled);
    const prefs = { ...loadPreferences(), focusIndicator: enabled };
    savePreferences(prefs);
    
    const root = document.documentElement;
    if (enabled) {
      root.classList.remove('no-focus-indicator');
    } else {
      root.classList.add('no-focus-indicator');
    }
    
    announceToScreenReader(
      enabled ? 'Focus indicators enabled' : 'Focus indicators disabled'
    );
  };

  const runAudit = () => {
    const results = runA11yAudit();
    setAuditResults(results);
    announceToScreenReader(
      results.valid 
        ? 'Accessibility audit passed'
        : `Accessibility audit found ${results.issues.length} issue categories`
    );
  };

  const resetToDefaults = () => {
    const defaults = {
      reducedMotion: prefersReducedMotion(),
      highContrast: false,
      fontSize: 16,
      keyboardNav: true,
      focusIndicator: true,
    };
    
    setReducedMotion(defaults.reducedMotion);
    setHighContrast(defaults.highContrast);
    setFontSize(defaults.fontSize);
    setKeyboardNav(defaults.keyboardNav);
    setFocusIndicator(defaults.focusIndicator);
    
    savePreferences(defaults);
    applyAccessibilitySettings(defaults);
    announceToScreenReader('Settings reset to defaults');
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Visual Preferences</CardTitle>
          <CardDescription>
            Customize the visual appearance for better accessibility
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Contrast className="h-4 w-4" />
                <div>
                  <Label htmlFor="high-contrast">High Contrast Mode</Label>
                  <p className="text-xs text-muted-foreground">
                    Increase contrast for better visibility
                  </p>
                </div>
              </div>
              <Switch
                id="high-contrast"
                checked={highContrast}
                onCheckedChange={handleHighContrastToggle}
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="font-size">Font Size</Label>
                <Badge variant="secondary">{fontSize}px</Badge>
              </div>
              <Slider
                id="font-size"
                min={12}
                max={24}
                step={1}
                value={[fontSize]}
                onValueChange={handleFontSizeChange}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Adjust text size across the application
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Motion & Animation</CardTitle>
          <CardDescription>
            Control animations and transitions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {reducedMotion ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              <div>
                <Label htmlFor="reduced-motion">Reduce Motion</Label>
                <p className="text-xs text-muted-foreground">
                  Minimize animations and transitions
                </p>
              </div>
            </div>
            <Switch
              id="reduced-motion"
              checked={reducedMotion}
              onCheckedChange={handleReducedMotionToggle}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Navigation</CardTitle>
          <CardDescription>
            Keyboard and focus management options
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Keyboard className="h-4 w-4" />
              <div>
                <Label htmlFor="keyboard-nav">Enhanced Keyboard Navigation</Label>
                <p className="text-xs text-muted-foreground">
                  Improved keyboard shortcuts and navigation
                </p>
              </div>
            </div>
            <Switch
              id="keyboard-nav"
              checked={keyboardNav}
              onCheckedChange={handleKeyboardNavToggle}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MousePointer className="h-4 w-4" />
              <div>
                <Label htmlFor="focus-indicator">Visible Focus Indicators</Label>
                <p className="text-xs text-muted-foreground">
                  Show outlines around focused elements
                </p>
              </div>
            </div>
            <Switch
              id="focus-indicator"
              checked={focusIndicator}
              onCheckedChange={handleFocusIndicatorToggle}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Accessibility Audit</CardTitle>
          <CardDescription>
            Check the current page for accessibility issues
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button onClick={runAudit} className="w-full">
            <Eye className="h-4 w-4 mr-2" />
            Run Accessibility Audit
          </Button>

          {auditResults && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {auditResults.valid ? (
                  <>
                    <CheckCircle className="h-5 w-5 text-green-500" />
                    <span className="font-medium text-green-700">No issues found</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="h-5 w-5 text-yellow-500" />
                    <span className="font-medium text-yellow-700">
                      {auditResults.issues.length} issue categories found
                    </span>
                  </>
                )}
              </div>

              {!auditResults.valid && (
                <div className="space-y-2 pl-7">
                  {auditResults.issues.map((category, idx) => (
                    <div key={idx} className="text-sm">
                      <p className="font-medium">{category.category}:</p>
                      <ul className="list-disc list-inside pl-4 text-muted-foreground">
                        {category.issues.map((issue: string, issueIdx: number) => (
                          <li key={issueIdx}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Button variant="outline" onClick={resetToDefaults} className="w-full">
        Reset to Defaults
      </Button>
    </div>
  );
}

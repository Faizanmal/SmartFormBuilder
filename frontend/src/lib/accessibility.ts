/**
 * Accessibility utilities and helpers for WCAG 2.1 AA compliance
 */

// Keyboard navigation helpers
export const KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  TAB: 'Tab',
  HOME: 'Home',
  END: 'End',
  PAGE_UP: 'PageUp',
  PAGE_DOWN: 'PageDown',
};

// Screen reader announcements
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

// Focus management
export function trapFocus(element: HTMLElement) {
  const focusableElements = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== KEYS.TAB) return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        lastFocusable.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        firstFocusable.focus();
        e.preventDefault();
      }
    }
  };

  element.addEventListener('keydown', handleTabKey);

  return () => {
    element.removeEventListener('keydown', handleTabKey);
  };
}

export function restoreFocus(previousElement: HTMLElement | null) {
  if (previousElement && document.body.contains(previousElement)) {
    previousElement.focus();
  }
}

// Color contrast checking (WCAG AA: 4.5:1 for normal text, 3:1 for large text)
export function getContrastRatio(foreground: string, background: string): number {
  const luminance1 = getRelativeLuminance(foreground);
  const luminance2 = getRelativeLuminance(background);

  const lighter = Math.max(luminance1, luminance2);
  const darker = Math.min(luminance1, luminance2);

  return (lighter + 0.05) / (darker + 0.05);
}

function getRelativeLuminance(color: string): number {
  const rgb = hexToRgb(color);
  if (!rgb) return 0;

  const [r, g, b] = [rgb.r, rgb.g, rgb.b].map((val) => {
    const s = val / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });

  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

export function meetsWCAGAA(foreground: string, background: string, isLargeText = false): boolean {
  const ratio = getContrastRatio(foreground, background);
  return isLargeText ? ratio >= 3 : ratio >= 4.5;
}

export function meetsWCAGAAA(foreground: string, background: string, isLargeText = false): boolean {
  const ratio = getContrastRatio(foreground, background);
  return isLargeText ? ratio >= 4.5 : ratio >= 7;
}

// Reduced motion detection
export function prefersReducedMotion(): boolean {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function setupReducedMotionListener(callback: (reduced: boolean) => void) {
  const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  
  callback(mediaQuery.matches);
  
  const handler = (e: MediaQueryListEvent) => callback(e.matches);
  mediaQuery.addEventListener('change', handler);
  
  return () => mediaQuery.removeEventListener('change', handler);
}

// High contrast mode detection
export function prefersHighContrast(): boolean {
  return (
    window.matchMedia('(prefers-contrast: high)').matches ||
    window.matchMedia('(-ms-high-contrast: active)').matches
  );
}

// Screen reader detection
export function isScreenReaderActive(): boolean {
  // This is not 100% reliable but provides a best guess
  return (
    navigator.userAgent.includes('JAWS') ||
    navigator.userAgent.includes('NVDA') ||
    navigator.userAgent.includes('VoiceOver')
  );
}

// Heading structure validation
export function validateHeadingStructure(): { valid: boolean; issues: string[] } {
  const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
  const issues: string[] = [];

  // Check for single h1
  const h1Count = headings.filter((h) => h.tagName === 'H1').length;
  if (h1Count === 0) {
    issues.push('No h1 heading found');
  } else if (h1Count > 1) {
    issues.push(`Multiple h1 headings found (${h1Count})`);
  }

  // Check for skipped levels
  for (let i = 1; i < headings.length; i++) {
    const currentLevel = parseInt(headings[i].tagName[1]);
    const previousLevel = parseInt(headings[i - 1].tagName[1]);

    if (currentLevel - previousLevel > 1) {
      issues.push(
        `Heading level skipped: ${headings[i - 1].tagName} -> ${headings[i].tagName}`
      );
    }
  }

  return {
    valid: issues.length === 0,
    issues,
  };
}

// Alt text validation
export function validateAltText(): { valid: boolean; issues: string[] } {
  const images = Array.from(document.querySelectorAll('img'));
  const issues: string[] = [];

  images.forEach((img, index) => {
    if (!img.hasAttribute('alt')) {
      issues.push(`Image ${index + 1} missing alt attribute: ${img.src}`);
    } else if (img.alt === '' && !img.hasAttribute('role')) {
      // Empty alt is okay for decorative images with role="presentation"
      issues.push(`Image ${index + 1} has empty alt text but no role="presentation"`);
    }
  });

  return {
    valid: issues.length === 0,
    issues,
  };
}

// Form label validation
export function validateFormLabels(): { valid: boolean; issues: string[] } {
  const inputs = Array.from(
    document.querySelectorAll('input:not([type="hidden"]), select, textarea')
  );
  const issues: string[] = [];

  inputs.forEach((input) => {
    const id = input.id;
    const ariaLabel = input.getAttribute('aria-label');
    const ariaLabelledBy = input.getAttribute('aria-labelledby');
    const label = id ? document.querySelector(`label[for="${id}"]`) : null;

    if (!label && !ariaLabel && !ariaLabelledBy) {
      issues.push(`Form field missing label: ${input.tagName} ${input.name || input.id || '(unnamed)'}`);
    }
  });

  return {
    valid: issues.length === 0,
    issues,
  };
}

// ARIA validation
export function validateAria(): { valid: boolean; issues: string[] } {
  const issues: string[] = [];

  // Check for aria-hidden on focusable elements
  const hiddenFocusable = document.querySelectorAll(
    '[aria-hidden="true"] button, [aria-hidden="true"] [href], [aria-hidden="true"] input, [aria-hidden="true"] select, [aria-hidden="true"] textarea'
  );

  if (hiddenFocusable.length > 0) {
    issues.push(`${hiddenFocusable.length} focusable elements are aria-hidden`);
  }

  // Check for invalid aria-labelledby references
  const labelledByElements = document.querySelectorAll('[aria-labelledby]');
  labelledByElements.forEach((el) => {
    const ids = el.getAttribute('aria-labelledby')?.split(' ') || [];
    ids.forEach((id) => {
      if (!document.getElementById(id)) {
        issues.push(`aria-labelledby references non-existent id: ${id}`);
      }
    });
  });

  return {
    valid: issues.length === 0,
    issues,
  };
}

// Skip link helper
export function createSkipLink(targetId: string, text = 'Skip to main content'): HTMLAnchorElement {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.textContent = text;
  skipLink.className = 'skip-link';
  skipLink.style.cssText = `
    position: absolute;
    left: -9999px;
    top: 0;
    z-index: 999;
    padding: 1em;
    background: #000;
    color: #fff;
    text-decoration: none;
  `;

  skipLink.addEventListener('focus', () => {
    skipLink.style.left = '0';
  });

  skipLink.addEventListener('blur', () => {
    skipLink.style.left = '-9999px';
  });

  return skipLink;
}

// Live region helpers
export function createLiveRegion(id: string, mode: 'polite' | 'assertive' = 'polite'): HTMLDivElement {
  const liveRegion = document.createElement('div');
  liveRegion.id = id;
  liveRegion.setAttribute('role', 'status');
  liveRegion.setAttribute('aria-live', mode);
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.className = 'sr-only';

  return liveRegion;
}

export function updateLiveRegion(id: string, message: string) {
  const liveRegion = document.getElementById(id);
  if (liveRegion) {
    liveRegion.textContent = message;
  }
}

// Run full accessibility audit
export function runA11yAudit(): {
  valid: boolean;
  issues: Array<{ category: string; issues: string[] }>;
} {
  const results = [
    { category: 'Heading Structure', ...validateHeadingStructure() },
    { category: 'Alt Text', ...validateAltText() },
    { category: 'Form Labels', ...validateFormLabels() },
    { category: 'ARIA', ...validateAria() },
  ];

  const allIssues = results.filter((r) => !r.valid);

  return {
    valid: allIssues.length === 0,
    issues: allIssues.map((r) => ({ category: r.category, issues: r.issues })),
  };
}

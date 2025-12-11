"""
Theme and branding service
"""
from typing import Dict, List
import re


class ThemeService:
    """Handle custom themes and branding"""
    
    def create_theme(
        self,
        user,
        name: str,
        colors: Dict,
        typography: Dict,
        layout: Dict,
        **kwargs
    ) -> Dict:
        """Create new theme"""
        from ..models_themes import Theme
        
        try:
            theme = Theme.objects.create(
                user=user,
                name=name,
                colors=colors,
                typography=typography,
                layout=layout,
                **kwargs
            )
            
            # Validate theme
            validation = self.validate_theme(theme)
            
            return {
                'success': True,
                'theme_id': str(theme.id),
                'validation': validation
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_theme(self, theme) -> Dict:
        """Validate theme for accessibility and brand guidelines"""
        issues = []
        warnings = []
        
        # Check color contrast
        colors = theme.colors
        if 'text' in colors and 'background' in colors:
            contrast = self._calculate_contrast_ratio(
                colors['text'],
                colors['background']
            )
            
            if contrast < 4.5:
                issues.append(f'Low contrast ratio: {contrast:.2f} (minimum 4.5:1 for WCAG AA)')
        
        # Check if brand guidelines are enforced
        if theme.enforce_guidelines and theme.brand_guidelines:
            guidelines = theme.brand_guidelines
            
            # Check required colors
            if 'required_colors' in guidelines:
                for required_color in guidelines['required_colors']:
                    color_found = any(
                        self._colors_match(required_color, color_value)
                        for color_value in colors.values()
                    )
                    if not color_found:
                        warnings.append(f'Required brand color {required_color} not used')
            
            # Check forbidden colors
            if 'forbidden_colors' in guidelines:
                for forbidden_color in guidelines['forbidden_colors']:
                    color_found = any(
                        self._colors_match(forbidden_color, color_value)
                        for color_value in colors.values()
                    )
                    if color_found:
                        issues.append(f'Forbidden brand color {forbidden_color} used')
        
        # Validate CSS safety
        if theme.custom_css:
            css_issues = self._validate_custom_css(theme.custom_css)
            issues.extend(css_issues)
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def relative_luminance(rgb):
            r, g, b = [x / 255.0 for x in rgb]
            r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
            g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
            b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        try:
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            l1 = relative_luminance(rgb1)
            l2 = relative_luminance(rgb2)
            
            lighter = max(l1, l2)
            darker = min(l1, l2)
            
            return (lighter + 0.05) / (darker + 0.05)
        except:
            return 0
    
    def _colors_match(self, color1: str, color2: str, tolerance: int = 10) -> bool:
        """Check if two colors match within tolerance"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        try:
            rgb1 = hex_to_rgb(color1)
            rgb2 = hex_to_rgb(color2)
            
            # Calculate Euclidean distance
            distance = sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)) ** 0.5
            
            return distance <= tolerance
        except:
            return False
    
    def _validate_custom_css(self, css: str) -> List[str]:
        """Validate custom CSS for security issues"""
        issues = []
        
        # Block dangerous CSS
        dangerous_patterns = [
            r'javascript:',
            r'<script',
            r'expression\s*\(',
            r'@import',
            r'behavior:',
            r'-moz-binding',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, css, re.IGNORECASE):
                issues.append(f'Dangerous CSS pattern detected: {pattern}')
        
        return issues
    
    def generate_mobile_theme(self, theme_id: str) -> Dict:
        """Generate mobile-optimized version of theme"""
        from ..models_themes import Theme
        
        try:
            theme = Theme.objects.get(id=theme_id)
            
            mobile_overrides = {
                'colors': theme.colors.copy(),
                'typography': {
                    **theme.typography,
                    'fontSize': '14px',  # Slightly smaller for mobile
                },
                'layout': {
                    **theme.layout,
                    'borderRadius': theme.layout.get('borderRadius', '8px'),
                    'spacing': 'compact',
                    'containerWidth': '100%',
                    'fieldSpacing': '16px',  # Tighter spacing on mobile
                },
                'components': {
                    **theme.components,
                    'button': {'size': 'large', 'style': 'solid'},  # Larger buttons for touch
                    'input': {'size': 'large', 'variant': 'outlined'},
                }
            }
            
            return {
                'success': True,
                'mobile_theme': mobile_overrides
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def apply_theme_to_form(self, form_id: str, theme_id: str, overrides: Dict = None) -> Dict:
        """Apply theme to a form"""
        from ..models_themes import FormTheme, Theme
        from ..models import Form
        
        try:
            form = Form.objects.get(id=form_id)
            theme = Theme.objects.get(id=theme_id)
            
            form_theme, created = FormTheme.objects.get_or_create(
                form=form,
                defaults={
                    'theme': theme,
                    'color_overrides': overrides.get('colors', {}) if overrides else {},
                    'typography_overrides': overrides.get('typography', {}) if overrides else {},
                    'layout_overrides': overrides.get('layout', {}) if overrides else {},
                }
            )
            
            if not created:
                form_theme.theme = theme
                if overrides:
                    form_theme.color_overrides = overrides.get('colors', {})
                    form_theme.typography_overrides = overrides.get('typography', {})
                    form_theme.layout_overrides = overrides.get('layout', {})
                form_theme.save()
            
            return {
                'success': True,
                'form_theme_id': str(form_theme.id)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_compiled_theme(self, form_id: str) -> Dict:
        """Get compiled theme with all overrides applied"""
        from ..models_themes import FormTheme
        
        try:
            form_theme = FormTheme.objects.get(form_id=form_id)
            
            if not form_theme.theme:
                return {'success': False, 'error': 'No theme assigned'}
            
            # Start with base theme
            compiled = {
                'colors': form_theme.theme.colors.copy(),
                'typography': form_theme.theme.typography.copy(),
                'layout': form_theme.theme.layout.copy(),
                'components': form_theme.theme.components.copy(),
                'custom_css': form_theme.theme.custom_css,
                'custom_js': form_theme.theme.custom_js,
            }
            
            # Apply form-specific overrides
            if form_theme.color_overrides:
                compiled['colors'].update(form_theme.color_overrides)
            if form_theme.typography_overrides:
                compiled['typography'].update(form_theme.typography_overrides)
            if form_theme.layout_overrides:
                compiled['layout'].update(form_theme.layout_overrides)
            
            return {
                'success': True,
                'theme': compiled
            }
        except FormTheme.DoesNotExist:
            return {'success': False, 'error': 'No theme configured for this form'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_marketplace_themes(
        self,
        category: str = None,
        min_rating: float = 0,
        is_premium: bool = None
    ) -> List[Dict]:
        """Search theme marketplace"""
        from ..models_themes import Theme
        
        themes = Theme.objects.filter(is_public=True, is_active=True)
        
        if min_rating:
            themes = themes.filter(rating_average__gte=min_rating)
        
        if is_premium is not None:
            themes = themes.filter(is_premium=is_premium)
        
        themes = themes.order_by('-downloads_count', '-rating_average')
        
        return [
            {
                'id': str(theme.id),
                'name': theme.name,
                'description': theme.description,
                'preview_image': theme.preview_image_url,
                'rating': float(theme.rating_average),
                'downloads': theme.downloads_count,
                'is_premium': theme.is_premium,
                'colors': theme.colors,
            }
            for theme in themes[:50]  # Limit to 50 results
        ]
    
    def rate_theme(self, theme_id: str, user, rating: int, review: str = '') -> Dict:
        """Rate a marketplace theme"""
        from ..models_themes import Theme, ThemeRating
        
        try:
            theme = Theme.objects.get(id=theme_id)
            
            rating_obj, created = ThemeRating.objects.update_or_create(
                theme=theme,
                user=user,
                defaults={
                    'rating': rating,
                    'review': review
                }
            )
            
            # Recalculate theme average rating
            all_ratings = ThemeRating.objects.filter(theme=theme)
            theme.rating_average = sum(r.rating for r in all_ratings) / all_ratings.count()
            theme.rating_count = all_ratings.count()
            theme.save()
            
            return {
                'success': True,
                'new_average': float(theme.rating_average)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

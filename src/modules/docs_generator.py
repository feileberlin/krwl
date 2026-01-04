"""
Documentation Generator Module

Generates styled HTML documentation from Markdown files in docs/ directory.
Uses the application's Barbie Pink color scheme and Lucide icons.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List
import markdown
from pygments.formatters import HtmlFormatter

# Configure module logger
logger = logging.getLogger(__name__)


class DocsGenerator:
    """Generates styled documentation from Markdown files"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.docs_source_path = self.base_path / 'docs'
        self.docs_output_path = self.base_path / 'public' / 'docs'
        self.assets_path = self.base_path / 'assets'
        self.config_path = self.base_path / 'config.json'
        
        # Ensure output directory exists
        self.docs_output_path.mkdir(parents=True, exist_ok=True)
        
        # Load config for design tokens
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        
        # Configure Markdown processor
        self.md = markdown.Markdown(extensions=[
            'extra',  # Tables, fenced code blocks, etc.
            'codehilite',  # Syntax highlighting
            'toc',  # Table of contents
            'meta',  # Metadata
            'sane_lists'  # Better list handling
        ])
    
    def get_doc_files(self) -> List[Path]:
        """Get all Markdown files in docs directory"""
        return sorted(self.docs_source_path.glob('*.md'))
    
    def generate_docs_css(self) -> str:
        """Generate CSS for documentation using design tokens"""
        colors = self.config['design']['colors']
        typography = self.config['design']['typography']
        spacing = self.config['design']['spacing']
        borders = self.config['design']['borders']
        shadows = self.config['design']['shadows']
        
        # Generate Pygments CSS for syntax highlighting
        formatter = HtmlFormatter(style='monokai')
        pygments_css = formatter.get_style_defs('.codehilite')
        
        css = f"""
/* Documentation Styles - Generated from config.json design tokens */

:root {{
    /* Colors from design tokens */
    --color-primary: {colors['primary']};
    --color-primary-hover: {colors['primary_hover']};
    --color-bg-primary: {colors['bg_primary']};
    --color-bg-secondary: {colors['bg_secondary']};
    --color-bg-tertiary: {colors['bg_tertiary']};
    --color-text-primary: {colors['text_primary']};
    --color-text-secondary: {colors['text_secondary']};
    --color-text-tertiary: {colors['text_tertiary']};
    --color-border-primary: {colors['border_primary']};
    --color-border-secondary: {colors['border_secondary']};
    --color-accent: {colors['accent']};
    --color-success: {colors['success']};
    --color-warning: {colors['warning']};
    --color-error: {colors['error']};
    
    /* Typography */
    --font-family-base: {typography['font_family_base']};
    --font-family-mono: {typography['font_family_mono']};
    --font-size-base: {typography['font_size_base']};
    --font-size-small: {typography['font_size_small']};
    --font-size-large: {typography['font_size_large']};
    --line-height-base: {typography['line_height_base']};
    
    /* Spacing */
    --spacing-sm: {spacing['sm']};
    --spacing-md: {spacing['md']};
    --spacing-lg: {spacing['lg']};
    --spacing-xl: {spacing['xl']};
    --spacing-xxl: {spacing['xxl']};
    
    /* Borders */
    --border-radius-small: {borders['radius_small']};
    --border-radius-medium: {borders['radius_medium']};
    --border-radius-large: {borders['radius_large']};
    
    /* Shadows */
    --shadow-small: {shadows['small']};
    --shadow-medium: {shadows['medium']};
    --shadow-large: {shadows['large']};
    --shadow-glow-primary: {shadows['glow_primary']};
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-family-base);
    background: var(--color-bg-primary);
    color: var(--color-text-primary);
    line-height: var(--line-height-base);
    font-size: var(--font-size-base);
}}

/* Layout */
.docs-container {{
    display: flex;
    min-height: 100vh;
}}

/* Sidebar Navigation */
.docs-sidebar {{
    width: 280px;
    background: var(--color-bg-secondary);
    border-right: 1px solid var(--color-border-primary);
    padding: var(--spacing-lg);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
}}

.docs-logo {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--color-border-primary);
}}

.docs-logo-icon {{
    color: var(--color-primary);
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}}

.docs-logo-icon svg {{
    width: 32px;
    height: 32px;
}}

.docs-logo-text {{
    font-size: var(--font-size-large);
    font-weight: 600;
    color: var(--color-primary);
}}

.docs-nav {{
    list-style: none;
}}

.docs-nav-item {{
    margin-bottom: var(--spacing-sm);
}}

.docs-nav-link {{
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    color: var(--color-text-secondary);
    text-decoration: none;
    border-radius: var(--border-radius-small);
    transition: all 0.2s ease;
}}

.docs-nav-link:hover {{
    background: var(--color-bg-tertiary);
    color: var(--color-text-primary);
}}

.docs-nav-link.active {{
    background: var(--color-bg-tertiary);
    color: var(--color-primary);
    border-left: 2px solid var(--color-primary);
}}

.docs-nav-icon {{
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}}

.docs-nav-icon svg {{
    width: 18px;
    height: 18px;
}}

/* Main Content */
.docs-main {{
    margin-left: 280px;
    flex: 1;
    padding: var(--spacing-xl);
    max-width: 900px;
}}

.docs-content {{
    background: var(--color-bg-secondary);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-xxl);
    box-shadow: var(--shadow-medium);
}}

/* Back to App Link */
.back-to-app {{
    display: inline-flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--color-accent);
    text-decoration: none;
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-small);
    transition: color 0.2s ease;
}}

.back-to-app:hover {{
    color: var(--color-primary);
}}

/* Typography */
.docs-content h1 {{
    color: var(--color-primary);
    font-size: 2.5rem;
    margin-bottom: var(--spacing-lg);
    padding-bottom: var(--spacing-md);
    border-bottom: 2px solid var(--color-border-primary);
}}

.docs-content h2 {{
    color: var(--color-text-primary);
    font-size: 2rem;
    margin-top: var(--spacing-xl);
    margin-bottom: var(--spacing-md);
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
}}

.docs-content h2::before {{
    content: '';
    width: 4px;
    height: 1.5rem;
    background: var(--color-primary);
    border-radius: 2px;
}}

.docs-content h3 {{
    color: var(--color-text-primary);
    font-size: 1.5rem;
    margin-top: var(--spacing-lg);
    margin-bottom: var(--spacing-md);
}}

.docs-content h4 {{
    color: var(--color-text-secondary);
    font-size: 1.25rem;
    margin-top: var(--spacing-md);
    margin-bottom: var(--spacing-sm);
}}

.docs-content p {{
    margin-bottom: var(--spacing-md);
    color: var(--color-text-primary);
}}

.docs-content a {{
    color: var(--color-accent);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s ease;
}}

.docs-content a:hover {{
    border-bottom-color: var(--color-accent);
}}

/* Lists */
.docs-content ul,
.docs-content ol {{
    margin-bottom: var(--spacing-md);
    padding-left: var(--spacing-xl);
}}

.docs-content li {{
    margin-bottom: var(--spacing-sm);
    color: var(--color-text-primary);
}}

/* Code */
.docs-content code {{
    font-family: var(--font-family-mono);
    background: var(--color-bg-tertiary);
    padding: 2px 6px;
    border-radius: var(--border-radius-small);
    font-size: var(--font-size-small);
    color: var(--color-primary);
}}

.docs-content pre {{
    background: var(--color-bg-tertiary);
    border: 1px solid var(--color-border-primary);
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
    overflow-x: auto;
}}

.docs-content pre code {{
    background: none;
    padding: 0;
    color: var(--color-text-primary);
}}

/* Tables */
.docs-content table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: var(--spacing-md);
    background: var(--color-bg-tertiary);
    border-radius: var(--border-radius-medium);
    overflow: hidden;
}}

.docs-content th {{
    background: var(--color-bg-primary);
    color: var(--color-primary);
    padding: var(--spacing-md);
    text-align: left;
    font-weight: 600;
}}

.docs-content td {{
    padding: var(--spacing-md);
    border-top: 1px solid var(--color-border-primary);
    color: var(--color-text-primary);
}}

.docs-content tr:hover td {{
    background: var(--color-bg-secondary);
}}

/* Blockquotes */
.docs-content blockquote {{
    border-left: 4px solid var(--color-primary);
    padding-left: var(--spacing-md);
    margin: var(--spacing-md) 0;
    color: var(--color-text-secondary);
    font-style: italic;
    background: var(--color-bg-tertiary);
    padding: var(--spacing-md);
    border-radius: var(--border-radius-small);
}}

/* Horizontal Rule */
.docs-content hr {{
    border: none;
    height: 1px;
    background: var(--color-border-primary);
    margin: var(--spacing-lg) 0;
}}

/* Syntax Highlighting */
{pygments_css}

.codehilite {{
    background: var(--color-bg-tertiary) !important;
    border-radius: var(--border-radius-medium);
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}}

/* Mobile Responsiveness */
@media (max-width: 768px) {{
    .docs-sidebar {{
        display: none;
    }}
    
    .docs-main {{
        margin-left: 0;
        padding: var(--spacing-md);
    }}
    
    .docs-content {{
        padding: var(--spacing-md);
    }}
    
    .docs-content h1 {{
        font-size: 2rem;
    }}
    
    .docs-content h2 {{
        font-size: 1.5rem;
    }}
}}

/* Scrollbar Styling */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--color-bg-primary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--color-border-primary);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--color-primary);
}}
"""
        return css
    
    def get_icon_svg(self, icon_name: str) -> str:
        """Get inline SVG for Lucide icon"""
        # Lucide icon SVG paths - minimal set for documentation
        icons = {
            'book-open': '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
            'git-branch': '<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
            'palette': '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
            'package': '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
            'zap': '<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',
            'check-circle': '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="m9 11 3 3L22 4"/>',
            'heart': '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
            'map': '<path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/><path d="M15 5.764v15"/><path d="M9 3.236v15"/>',
            'smile': '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/>',
            'file-text': '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
            'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
            'code': '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
            'bookmark': '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
            'folder': '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
            'arrow-left': '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
        }
        
        svg_path = icons.get(icon_name, icons['file-text'])
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg_path}</svg>'
    
    def get_icon_for_file(self, filename: str) -> str:
        """Get appropriate Lucide icon for documentation file"""
        icon_map = {
            'CHANGELOG': 'git-branch',
            'COLOR_SCHEME': 'palette',
            'DEPENDENCY': 'package',
            'EASY': 'zap',
            'IMPLEMENTATION': 'check-circle',
            'KISS': 'heart',
            'LEAFLET': 'map',
            'LUCIDE': 'smile',
            'MARKDOWN': 'file-text',
            'PROOF': 'shield-check',
            'PYTHON': 'code',
            'QUICK_REFERENCE': 'bookmark',
            'SSG': 'folder',
        }
        
        for key, icon in icon_map.items():
            if key in filename.upper():
                return icon
        
        return 'file-text'  # Default icon
    
    def generate_navigation(self, doc_files: List[Path], current_file: Path = None) -> str:
        """Generate navigation HTML with inline Lucide SVG icons"""
        nav_items = []
        
        for doc_file in doc_files:
            filename = doc_file.stem
            icon_name = self.get_icon_for_file(filename)
            icon_svg = self.get_icon_svg(icon_name)
            # Convert filename to title (e.g., CHANGELOG -> Changelog)
            title = filename.replace('_', ' ').title()
            output_filename = f"{filename}.html"
            
            active_class = ' active' if current_file and doc_file == current_file else ''
            
            nav_items.append(f'''
            <li class="docs-nav-item">
                <a href="{output_filename}" class="docs-nav-link{active_class}">
                    <span class="docs-nav-icon">{icon_svg}</span>
                    <span>{title}</span>
                </a>
            </li>
            ''')
        
        return '\n'.join(nav_items)
    
    def generate_html(self, doc_file: Path, content_html: str, navigation: str) -> str:
        """Generate complete HTML document"""
        filename = doc_file.stem
        title = filename.replace('_', ' ').title()
        css = self.generate_docs_css()
        
        # Get inline SVG for logo icon
        logo_svg = self.get_icon_svg('book-open')
        arrow_svg = self.get_icon_svg('arrow-left')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - KRWL HOF Documentation</title>
    <meta name="description" content="KRWL HOF Community Events Documentation">
    <style>
{css}
    </style>
</head>
<body>
    <div class="docs-container">
        <!-- Sidebar Navigation -->
        <nav class="docs-sidebar">
            <div class="docs-logo">
                <span class="docs-logo-icon">{logo_svg}</span>
                <span class="docs-logo-text">Docs</span>
            </div>
            <ul class="docs-nav">
{navigation}
            </ul>
        </nav>
        
        <!-- Main Content -->
        <main class="docs-main">
            <a href="../index.html" class="back-to-app">
                <span style="display: inline-flex; align-items: center; width: 18px; height: 18px;">{arrow_svg}</span>
                Back to App
            </a>
            <article class="docs-content">
{content_html}
            </article>
        </main>
    </div>
</body>
</html>"""
        return html
    
    def generate_index(self, doc_files: List[Path]) -> str:
        """Generate index page listing all documentation"""
        navigation = self.generate_navigation(doc_files)
        
        content_items = []
        for doc_file in doc_files:
            filename = doc_file.stem
            icon_name = self.get_icon_for_file(filename)
            icon_svg = self.get_icon_svg(icon_name)
            title = filename.replace('_', ' ').title()
            output_filename = f"{filename}.html"
            
            # Read first paragraph from markdown as description
            with open(doc_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                description = ''
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        description = line.strip()[:150] + '...' if len(line.strip()) > 150 else line.strip()
                        break
            
            content_items.append(f'''
            <div style="background: var(--color-bg-tertiary); padding: var(--spacing-lg); border-radius: var(--border-radius-medium); margin-bottom: var(--spacing-md);">
                <h3 style="margin-top: 0; display: flex; align-items: center; gap: var(--spacing-sm);">
                    <span style="color: var(--color-primary); width: 24px; height: 24px; display: inline-flex; flex-shrink: 0;">{icon_svg}</span>
                    <a href="{output_filename}" style="color: var(--color-text-primary); text-decoration: none;">{title}</a>
                </h3>
                <p style="color: var(--color-text-secondary); margin-bottom: 0;">{description}</p>
            </div>
            ''')
        
        content_html = f"""
        <h1>Documentation</h1>
        <p>Welcome to the KRWL HOF Community Events documentation. Select a topic to learn more:</p>
        {''.join(content_items)}
        """
        
        return self.generate_html(Path('index.md'), content_html, navigation)
    
    def generate_all(self):
        """Generate HTML for all Markdown documentation files"""
        logger.info("Generating documentation HTML from Markdown files...")
        
        doc_files = self.get_doc_files()
        if not doc_files:
            logger.warning("No documentation files found in docs/ directory")
            return
        
        logger.info(f"Found {len(doc_files)} documentation files")
        
        # Generate navigation HTML (same for all pages)
        navigation = self.generate_navigation(doc_files)
        
        # Generate each documentation page
        for doc_file in doc_files:
            logger.info(f"Processing {doc_file.name}...")
            
            # Read and convert Markdown to HTML
            with open(doc_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Reset markdown processor for new document
            self.md.reset()
            content_html = self.md.convert(markdown_content)
            
            # Generate navigation with current file highlighted
            current_nav = self.generate_navigation(doc_files, doc_file)
            
            # Generate complete HTML
            html = self.generate_html(doc_file, content_html, current_nav)
            
            # Write to output
            output_file = self.docs_output_path / f"{doc_file.stem}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Generated {output_file}")
        
        # Generate index page
        logger.info("Generating documentation index...")
        index_html = self.generate_index(doc_files)
        index_file = self.docs_output_path / 'index.html'
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        logger.info(f"Generated {index_file}")
        
        logger.info(f"Documentation generation complete! {len(doc_files)} pages created.")


def main():
    """Command-line interface for docs generator"""
    import sys
    import os
    
    # Get base path
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    # Generate documentation
    generator = DocsGenerator(base_path)
    generator.generate_all()


if __name__ == '__main__':
    main()

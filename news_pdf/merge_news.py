#!/usr/bin/env python3
"""
News Report Generator
A class-based system for generating HTML and PDF news reports with theme support.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from utils.logger import logger
from utils.read_write import read_text_file, write_text_file, read_json_file


class NewsReportGenerator:
    """
    A class for generating news reports with theme support.
    
    Handles the complete pipeline from data processing to PDF generation
    with automatic theme detection based on time or manual override.
    """
    
    # Theme configuration
    THEMES = {
        'morning': {
            'name': 'Morning',
            'icon': '☀️',
            'time_range': (6, 18)  # 6 AM to 6 PM
        },
        'evening': {
            'name': 'Evening', 
            'icon': '🌙',
            'time_range': (18, 6)  # 6 PM to 6 AM
        }
    }
    
    def __init__(self, template_file="news_pdf/template.html"):
        """
        Initialize the NewsReportGenerator.
        
        Args:
            template_file (str): Path to the HTML template file
        """
        self.template_file = template_file
        self._validate_files()
    
    def _validate_files(self):
        """Validate that required files exist."""
        required_files = [
            self.template_file,
            "news_pdf/style.css",
            "news_pdf/morning.css", 
            "news_pdf/evening.css"
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file not found: {file_path}")
    
    def _determine_theme(self, report_time='auto'):
        """
        Determine the appropriate theme based on time or override.
        
        Args:
            report_time (str): 'morning', 'evening', or 'auto'
            
        Returns:
            str: The determined theme ('morning' or 'evening')
        """
        if report_time in ['morning', 'evening']:
            return report_time
        
        # Auto-detect based on current time
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 18:
            return 'morning'
        else:
            return 'evening'
    
    def _merge_data_to_template(self, template, news_data, report_time='auto'):
        """
        Merge news data and theme into the HTML template.
        
        Args:
            template (str): HTML template content
            news_data (list): List of news items
            report_time (str): Theme preference
            
        Returns:
            str: Merged HTML content
        """
        try:
            # Convert news data to JSON string for JavaScript
            news_json = json.dumps(news_data, ensure_ascii=False, indent=2)
            
            # Determine theme
            theme = self._determine_theme(report_time)
            
            # Replace placeholders in template
            html_content = template.replace('{{NEWS_DATA}}', news_json)
            html_content = html_content.replace('{{REPORT_TIME}}', theme)
            
            logger.info(f"✅ Successfully merged {len(news_data)} news items with {theme} theme")
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Error merging news data: {e}")
            return None
    
    def generate_html_report(self, input_json, output_file, report_time='auto'):
        """
        Generate an HTML report from JSON data.
        
        Args:
            input_json (str): Path to JSON file with news data
            output_file (str): Path for the output HTML file
            report_time (str): Theme preference ('morning', 'evening', 'auto')
            
        Returns:
            str: Path to generated HTML file, or None if failed
        """
        try:
            # Read news data
            news_data = read_json_file(input_json)
            if not news_data:
                logger.error(f"❌ No news data found in {input_json}")
                return None
            
            # Read template
            template = read_text_file(self.template_file)
            if template is None:
                logger.error(f"❌ No template found in {self.template_file}")
                return None
            
            # Merge data into template
            merged_html = self._merge_data_to_template(template, news_data, report_time)
            if merged_html is None:
                return None
            
            # Save the generated HTML
            write_text_file(output_file, merged_html)
            logger.info(f"📄 HTML report saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"❌ Error generating HTML report: {e}")
            return None
    
    async def _convert_html_to_pdf(self, html_file_path, pdf_file_path):
        """
        Convert HTML file to PDF using Playwright.
        
        Args:
            html_file_path (str): Path to the HTML file
            pdf_file_path (str): Path for the output PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Convert file path to file URL
                file_url = f"file://{os.path.abspath(html_file_path)}"
                
                # Navigate to the HTML file
                await page.goto(file_url)
                
                # Wait for content to load
                await page.wait_for_load_state('networkidle')
                
                # Generate PDF with RTL support and better page break handling
                await page.pdf(
                    path=pdf_file_path,
                    format='A4',
                    print_background=True,

                    prefer_css_page_size=True
                )
                
                await browser.close()
            
            logger.info(f"✅ Successfully converted HTML to PDF: {pdf_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error converting HTML to PDF: {e}")
            return False
    
    async def generate_pdf_report(self, input_json, output_file, pdf_file, report_time='auto'):
        """
        Generate a complete PDF report from JSON data.
        
        Args:
            input_json (str): Path to JSON file with news data
            output_file (str): Path for the output HTML file
            pdf_file (str): Path for the output PDF file
            report_time (str): Theme preference ('morning', 'evening', 'auto')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate HTML first
            html_result = self.generate_html_report(input_json, output_file, report_time)
            if not html_result:
                return False
            
            # Convert to PDF
            return await self._convert_html_to_pdf(output_file, pdf_file)
            
        except Exception as e:
            logger.error(f"❌ Error generating PDF report: {e}")
            return False
    
    def get_theme_info(self, report_time='auto'):
        """
        Get information about the current theme.
        
        Args:
            report_time (str): Theme preference
            
        Returns:
            dict: Theme information including name and icon
        """
        theme = self._determine_theme(report_time)
        return {
            'theme': theme,
            'name': self.THEMES[theme]['name'],
            'icon': self.THEMES[theme]['icon']
        }


# Legacy functions for backward compatibility
def merge_news_to_html(template, news_data, report_time='auto'):
    """Legacy function - use NewsReportGenerator class instead."""
    generator = NewsReportGenerator()
    return generator._merge_data_to_template(template, news_data, report_time)


def generate_html_report(input_json, template_file, output_file, report_time='auto'):
    """Legacy function - use NewsReportGenerator class instead."""
    generator = NewsReportGenerator(template_file)
    return generator.generate_html_report(input_json, output_file, report_time)


async def generate_pdf_report(input_json, template_file, output_file, pdf_file, report_time='auto'):
    """Legacy function - use NewsReportGenerator class instead."""
    generator = NewsReportGenerator(template_file)
    return await generator.generate_pdf_report(input_json, output_file, pdf_file, report_time)


async def html_to_pdf(html_file_path, pdf_file_path, css_file_path=None):
    """Legacy function - use NewsReportGenerator class instead."""
    generator = NewsReportGenerator()
    return await generator._convert_html_to_pdf(html_file_path, pdf_file_path)


async def main():
    """Main function to run the news report generator."""
    logger.debug("🚀 News Report Generator")
    logger.debug("=" * 50)

    # Use relative paths from the root directory
    input_file = "news_pdf/news_data.json"
    output_file = "news_pdf/output.html"
    pdf_file = "news_pdf/output.pdf"

    # Create generator instance
    generator = NewsReportGenerator()
    
    # Get theme info
    theme_info = generator.get_theme_info('morning')
    logger.info(f"🌅 Using {theme_info['name']} theme ({theme_info['icon']})")

    # Generate the HTML report with morning theme
    result = generator.generate_html_report(input_file, output_file, 'morning')
    
    if result:
        logger.info(f"📄 HTML Report saved to: {result}")
        
        # Generate PDF if Playwright is available
        logger.info("🔄 Converting HTML to PDF...")
        if await generator.generate_pdf_report(input_file, output_file, pdf_file, 'morning'):
            logger.info(f"📄 PDF Report saved to: {pdf_file}")
        else:
            logger.error("❌ Failed to generate PDF")
    else:
        logger.error("❌ Failed to generate news report")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
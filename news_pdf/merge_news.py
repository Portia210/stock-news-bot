#!/usr/bin/env python3
"""
News HTML Generator
Reads news data from output.txt and generates an HTML report using the template.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from utils.logger import logger
from utils.read_write import read_text_file, write_text_file, read_json_file




def merge_news_to_html(template, news_data, report_time='auto'):

    try:
        # Convert news data to JSON string for JavaScript
        news_json = json.dumps(news_data, ensure_ascii=False, indent=2)
        
        # Replace the placeholders in the template
        html_content = template.replace('{{NEWS_DATA}}', news_json)
        html_content = html_content.replace('{{REPORT_TIME}}', report_time)
        
        logger.info(f"Successfully merged {len(news_data)} news items into HTML template with {report_time} theme")
        return html_content
        
    except Exception as e:
        logger.error(f"Error merging news data: {e}")
        return None


async def html_to_pdf(html_file_path, pdf_file_path, css_file_path=None):
    """
    Convert HTML file to PDF using Playwright.
    
    Args:
        html_file_path (str): Path to the HTML file
        pdf_file_path (str): Path for the output PDF file
        css_file_path (str): Path to the CSS file (optional, not needed as CSS is linked in HTML)
        
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
            
            # Generate PDF with RTL support
            await page.pdf(
                path=pdf_file_path,
                format='A4',
                print_background=True,
            )
            
            await browser.close()
        
        logger.info(f"✅ Successfully converted HTML to PDF: {pdf_file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error converting HTML to PDF: {e}")
        return False


def generate_html_report(input_json, template_file, output_file, report_time='auto'):

    # Read news data
    news_data = read_json_file(input_json)
    if not news_data:
        logger.error(f"No news data found in {input_json}")
        return None
    
    # Read template
    template = read_text_file(template_file)
    if template is None:
        logger.error(f"No template found in {template_file}")
        return None
    
    # Merge data into template
    merged_html = merge_news_to_html(template, news_data, report_time)
    if merged_html is None:
        logger.error(f"Failed to merge news data into HTML template")
        return None
    
    # Save the generated HTML
    write_text_file(output_file, merged_html)
    return str(output_file)

async def generate_pdf_report(input_json, template_file, output_file, pdf_file, report_time='auto'):
    """Generate a PDF report from the HTML file."""
    generate_html_report(input_json, template_file, output_file, report_time)
    await html_to_pdf(output_file, pdf_file)

async def main():
    """Main function to run the news report generator."""
    logger.debug("🚀 News Report Generator")
    logger.debug("=" * 50)

    # Use relative paths from the root directory
    input_file = "news_pdf/news_data.json"
    template_file = "news_pdf/template.html"
    output_file = "news_pdf/output.html"
    pdf_file = "news_pdf/output.pdf"

    # Generate the HTML report with morning theme
    result = generate_html_report(input_file, template_file, output_file, 'morning')
    
    if result:
        logger.info(f"📄 HTML Report saved to: {result}")
        
        # Generate PDF if Playwright is available
        logger.info("🔄 Converting HTML to PDF...")
        if await html_to_pdf(output_file, pdf_file):
            logger.info(f"📄 PDF Report saved to: {pdf_file}")
        else:
            logger.error("❌ Failed to generate PDF")
    
        
        # Try to open the HTML file in the default browser
        # try:
        #     import webbrowser
        #     webbrowser.open(f"file://{os.path.abspath(result)}")
        #     logger.info("🌐 Opened HTML in default browser")
        # except Exception as e:
        #     logger.error(f"Could not open in browser: {e}")
    else:
        logger.error("❌ Failed to generate news report")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
#!/usr/bin/env python3
"""
Theme System Demo
Demonstrates how to generate reports with different themes.
"""

import asyncio
from merge_news import NewsReportGenerator
from utils.logger import logger

async def demo_themes():
    """Demonstrate both morning and evening themes."""
    
    # Sample news data
    sample_news = [
        {
            "time": "14:30",
            "message": "דוגמה לחדשות בבוקר - שוק ההון מראה סימני התאוששות",
            "link": "https://example.com/news1"
        },
        {
            "time": "15:45", 
            "message": "עוד דוגמה של חדשות עם קישור למקור",
            "link": "https://example.com/news2"
        }
    ]
    
    # Save sample data
    import json
    with open("news_pdf/demo_news.json", "w", encoding="utf-8") as f:
        json.dump(sample_news, f, ensure_ascii=False, indent=2)
    
    logger.info("🎨 Theme System Demo")
    logger.info("=" * 50)
    
    # Create generator instance
    generator = NewsReportGenerator()
    
    time_settings = {
        "morning": "morning",   
        "evening": "evening",
        "auto": "auto"
    }
    

    # Generate evening theme
    evening_info = generator.get_theme_info(time_settings["evening"])
    logger.info(f"{evening_info['icon']} Generating {evening_info['name']} theme...")
    await generator.generate_pdf_report(
        input_json="news_pdf/demo_news.json",
        output_file="news_pdf/demo_evening.html", 
        pdf_file="news_pdf/demo_evening.pdf",
        report_time="evening"
    )
    

    logger.info("✅ Demo completed! Check the generated files:")
    logger.info("📄 Morning: news_pdf/demo_morning.html & news_pdf/demo_morning.pdf")
    logger.info("📄 Evening: news_pdf/demo_evening.html & news_pdf/demo_evening.pdf") 
    logger.info("📄 Auto: news_pdf/demo_auto.html & news_pdf/demo_auto.pdf")

if __name__ == "__main__":
    asyncio.run(demo_themes()) 
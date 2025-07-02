from investing_scraper.InvestingDataScraper import InvestingDataScraper
import json
import asyncio
import os
from investing_scraper.investing_variables import investing_variables

async def fetch_all_data(pages_names):
    investing_scraper = InvestingDataScraper()
    # Fetch all pages asynchronously
    payload_update = {
        "currentTab": investing_variables.time_ranges.today, 
        "timeZone": investing_variables.time_zones.eastern_time,
        "importance[]": [investing_variables.importance.high],
        }
    fetch_tasks = [investing_scraper.run(page_name, payload_update, True) for page_name in pages_names]
    events_by_dates = await asyncio.gather(*fetch_tasks)
    
    return events_by_dates

async def main():
    pages_names = ["economic_calendar", "earnings_calendar", "holiday_calendar"]

    # Fetch all data asynchronously
    await fetch_all_data(pages_names)
    


if __name__ == "__main__":
    asyncio.run(main())
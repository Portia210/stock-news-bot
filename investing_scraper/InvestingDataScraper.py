import requests
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils.logger import logger
import os
import pandas as pd
from config import config
from utils.read_write import read_json_file
from utils.safe_update_dict import safe_update_dict
import json
from investing_scraper.investing_variables import investing_variables


class InvestingDataScraper:
    def __init__(self):
        self.headers = read_json_file(f'investing_scraper/headers.json')
        logger.debug(f"Initialized investing scraper")
    
    @staticmethod
    def get_element_attirbutes(soup_element, attributes):
        for attribute in attributes:
            if attribute == "text":
                value = soup_element.text.strip()
            else:
                value = soup_element.get(attribute)
            if value:
                return value
        return None


    async def _fetch_table(self, page_name, payload_update: dict = {}):
        """Fetch and parse the webpage asynchronously"""
        logger.debug(f"Fetching table data for {page_name}")
        request_json = read_json_file(f'investing_scraper/requests_json/{page_name}.json')
        safe_update_dict(request_json["payload"], payload_update)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(request_json['url'], headers=self.headers, data=request_json["payload"]) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch page. Status code: {response.status}")
                    return None
                try:
                    json_response = await response.read()
                    table_html = json.loads(json_response).get("data", '') 

                    return table_html
                except Exception as e:
                    logger.error(f"Error parsing JSON: {str(e)}")
                    return None 


    def _process_table_data(self, page_name, table_html):
        """Process all rows in the table"""
        table_structure = read_json_file(f'investing_scraper/tables_stucture.json')[page_name]
        table_selectors = table_structure["table_selectors"]

        def proccess_tr(tr, table_selectors):
            """Extract data from a single row"""
            row_data = {}
            for item_name, selector in table_selectors.items():
                if item_name == "date":
                    continue
                try:
                    data_element = tr.select_one(selector["selector"])
                    if data_element:
                        row_data[item_name] = self.get_element_attirbutes(data_element, selector["attribute"])
                except Exception as e:
                    logger.error(f"Error processing {item_name}: {str(e)}")
            return row_data
        
        table_soup = BeautifulSoup(table_html, 'html.parser')   
        all_rows = table_soup.find_all('tr')

        events_by_date = {}
        current_events = []
        current_date = "unknown"
        
        for row in all_rows:
            date_element = row.select_one(table_selectors['date']['selector'])
            new_date = self.get_element_attirbutes(date_element, table_selectors['date']['attribute']) if date_element else None


            # add the previous events to the matching date
            if new_date:
                if current_events:
                    events_by_date[current_date] = current_events
                    current_events = []
                current_date = new_date
                
            # extract the events if if not a date tr, or if the date is inline
            if not new_date or table_structure["is_date_inline"]:
                proccessed_row = proccess_tr(row, table_selectors)
                if proccessed_row:
                    current_events.append(proccessed_row)
        
        if current_events:
            events_by_date[current_date] = current_events
        
        return events_by_date
    




    def _save_data(self, page_name, date, data):
        output_dir = os.path.join("data", "investing_scraper")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df = pd.DataFrame(data)
        df.to_csv(os.path.join(output_dir, f"{page_name}_{date}.csv"), index=False)




    
    async def run(self, page_name, payload_update: dict = {}, save_data: bool = False):
        table_html = await self._fetch_table(page_name, payload_update)
        if not table_html:
            logger.error(f"Failed to fetch table data for {page_name}")
            return None
        events_by_dates = self._process_table_data(page_name, table_html)
        if events_by_dates == {}:
            logger.error(f"No events found for {page_name}")
            return 

        if save_data:
            for date, events in events_by_dates.items():
                self._save_data(page_name, date, events)
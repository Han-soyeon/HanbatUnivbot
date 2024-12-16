import requests
from bs4 import BeautifulSoup
import logging

class BoardSource:
    def __init__(self, base_url: str, table_class: str = "board_list table table-default", pagination_class: str = "pagination"):
        """
        Initialize with the base URL, table class, and pagination class.
        :param base_url: The base URL for fetching data.
        :param table_class: The class name of the table container.
        :param pagination_class: The class name of the pagination container.
        """
        self.base_url = base_url
        self.table_class = table_class
        self.pagination_class = pagination_class

    def fetch_announcements(self) -> list[list[str]]:
        """
        Fetch all announcements across all pages.
        :return: A list of announcement data (list of lists).
        """
        announcements = []
        page = 1

        while True:
            try:
                # Request data for the current page
                url = f"{self.base_url}?pageIndex={page}"
                logging.info(f"Fetching URL: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                # Find the table container using the dynamic class name
                table = soup.find("table", class_=self.table_class)
                if not table:
                    logging.warning(f"No table found with class '{self.table_class}' on page {page}. Stopping fetch.")
                    break

                tbody = table.find("tbody")
                if not tbody:
                    logging.warning(f"No <tbody> found in the table on page {page}. Stopping fetch.")
                    break

                # Check for 'nodata' rows
                nodata = tbody.find("td", class_="nodata")
                if nodata:
                    logging.info(f"Reached 'nodata' on page {page}. Ending fetch.")
                    break

                rows = tbody.find_all("tr")
                if not rows:
                    logging.info(f"No rows found on page {page}. Ending fetch.")
                    break

                # Extract data for each row
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 5:  # Skip rows with insufficient columns
                        logging.warning(f"Skipping malformed row on page {page}: {row}")
                        continue

                    # Extract text and clean HTML entities
                    data = [col.get_text(strip=True) for col in cols[:5]]  # Keep only the first 5 columns

                    # Validate row data to ensure correct length
                    if len(data) != 5:
                        logging.warning(f"Skipping row with unexpected column count on page {page}: {data}")
                        continue

                    logging.debug(f"Row data (page {page}): {data}")  # 디버깅 로그 추가
                    announcements.append(data)

                # Log the data for the current page
                logging.info(f"Page {page}: Collected {len(announcements)} total rows so far.")

                # Check for pagination
                pagination = soup.find("div", class_=self.pagination_class)
                if not pagination:
                    logging.info("No pagination found. Ending fetch.")
                    break

                next_page = pagination.find("a", {"aria-label": "Next"})
                if not next_page or "disabled" in next_page.get("class", []):
                    logging.info("No more pages to fetch. Ending fetch.")
                    break

                page += 1  # Move to the next page

            except requests.Timeout:
                logging.error(f"Timeout error while fetching page {page}. Retrying...")
                continue  # Retry fetching the same page
            except requests.RequestException as e:
                logging.error(f"Network error on page {page}: {e}")
                break
            except Exception as e:
                logging.error(f"Unexpected error on page {page}: {e}")
                break

        # Ensure the returned announcements are consistent
        if not announcements:
            logging.warning("No announcements fetched. Returning empty list.")
        else:
            logging.info(f"Fetched total {len(announcements)} announcements.")
        return announcements

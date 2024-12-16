from src.reports.report_factory import ReportFactory
import logging


class ReportHandler:
    def __init__(self, cached_data: dict = None):
        """
        Initialize the ReportHandler with optional cached data.
        :param cached_data: A dictionary containing cached announcement data per department.
        """
        self.factory = ReportFactory()
        self.cached_data = cached_data if cached_data is not None else {}

    def update_cache(self, department: str, data: list[list[str]]):
        """
        Update the cached data for a specific department.
        :param department: The department name (e.g., "computer", "electrical").
        :param data: The announcement data to cache.
        """
        try:
            if not isinstance(data, list) or not all(isinstance(row, list) and len(row) == 5 for row in data):
                raise ValueError(f"Invalid data format for department '{department}': {data}")

            # Transform and update cache
            transformed_data = self._transform_data(data)
            self.cached_data[department] = transformed_data
            logging.info(f"Cache updated for department '{department}', total items: {len(transformed_data)}")
        except Exception as e:
            logging.error(f"Error updating cache for department '{department}': {e}")
            raise

    def _transform_data(self, raw_data: list[list[str]]) -> list[dict]:
        """
        Transform raw table data into a list of dictionaries.
        :param raw_data: List of table rows as lists of strings.
        :return: List of dictionaries with headers as keys.
        """
        headers = ["번호", "제목", "작성자", "조회수", "등록일"]
        transformed = []
        for row in raw_data:
            if len(row) == len(headers):
                transformed.append(dict(zip(headers, row)))
            else:
                logging.warning(f"Skipping malformed row: {row}")
        return transformed

    def generate_report(self, format: str, department: str) -> str:
        """
        Generate a report based on the specified format and department.
        :param format: The format of the report (e.g., "excel", "pdf").
        :param department: The department for which to generate the report.
        :return: The file path of the generated report.
        """
        try:
            # 캐시 데이터 확인
            logging.info(f"Generating report for department '{department}' in format '{format}'")
            if department not in self.cached_data:
                logging.error(f"Department '{department}' not found in cached_data.")
                return f"Error: No data available for department '{department}'."
            
            cached_data = self.cached_data[department]
            if not cached_data:
                logging.error(f"Cached data for department '{department}' is empty.")
                return f"Error: No data available for department '{department}'."
            
            logging.debug(f"Cached data for '{department}': {cached_data}")

            # 보고서 생성
            report = self.factory.create_report(format)
            if not report:
                raise ValueError(f"Report format '{format}' is not supported.")

            file_path = report.generate(cached_data)
            logging.info(f"Report successfully generated: {file_path}")
            return f"Report successfully generated: {file_path}"

        except ValueError as ve:
            logging.error(f"ValueError while generating report: {ve}")
            return f"Error: {str(ve)}"
        except Exception as e:
            logging.error(f"Unexpected error while generating report: {e}")
            return f"Error: An unexpected error occurred."

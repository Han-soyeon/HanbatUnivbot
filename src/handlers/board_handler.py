from src.boards.board_factory import BoardFactory
import logging

class BoardHandler:
    def __init__(self, shared_cache: dict = None):
        """
        Initialize the BoardHandler with optional shared cache.
        :param shared_cache: Shared cache to synchronize with other handlers (e.g., ReportHandler).
        """
        self.factory = BoardFactory()
        self.cached_data = shared_cache if shared_cache is not None else {}  # Shared or local cache

    def update_cache(self, department: str, data: list[list[str]]):
        """
        Update the cached data for a specific department.
        :param department: The department name (e.g., "computer", "electrical").
        :param data: The announcement data to cache.
        """
        try:
            if not isinstance(data, list) or not all(isinstance(row, list) and len(row) == 5 for row in data):
                raise ValueError(f"Invalid data format for department '{department}': {data}")

            # 캐시에 데이터 업데이트
            self.cached_data[department] = data
            logging.info(f"Cache updated for department '{department}', total items: {len(data)}")
        except Exception as e:
            logging.error(f"Error updating cache for department '{department}': {e}")
            raise

    def handle_request(self, department: str) -> list[list[str]]:
        """
        Handle request for fetching announcements for a department.
        Use cached data if available, otherwise fetch new data.
        :param department: The department name (e.g., "computer", "electrical").
        :return: List of announcement data.
        """
        try:
            logging.info(f"Handling request for department: '{department}'")

            # 캐시 데이터 확인
            if department in self.cached_data:
                cached_data = self.cached_data[department]
                if cached_data:
                    logging.info(f"Returning cached data for department '{department}', total items: {len(cached_data)}")
                    return cached_data
                else:
                    logging.warning(f"Cache exists for department '{department}', but it is empty.")

            # 새 데이터 가져오기
            board = self.factory.get_board(department)
            if not board:
                raise ValueError(f"Board not found for department '{department}'")

            announcements = board.fetch_announcements()

            # 데이터 검증
            if not isinstance(announcements, list) or not all(isinstance(row, list) and len(row) == 5 for row in announcements):
                raise ValueError(f"Invalid data fetched for department '{department}': {announcements}")

            # 캐시 업데이트 및 데이터 반환
            self.update_cache(department, announcements)
            return announcements

        except ValueError as ve:
            logging.error(f"ValueError while handling request for department '{department}': {ve}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error while handling request for department '{department}': {e}")
            return []

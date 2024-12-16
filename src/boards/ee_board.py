from src.boards.board_source import BoardSource
import logging

class EEBoard(BoardSource):
    def __init__(self):
        super().__init__(
            base_url="https://www.hanbat.ac.kr/prog/bbsArticle/BBSMSTR_000000000348/list.do",
            table_class="board_list table table-default",
            pagination_class="pagination"
        )

    def fetch_announcements(self):
        """
        EEBoard는 BoardSource의 fetch_announcements 메서드를 호출하여
        데이터를 가져옵니다.
        """
        announcements = super().fetch_announcements()
        if not announcements:
            logging.warning("EEBoard: No announcements found.")
        else:
            logging.info(f"EEBoard fetched {len(announcements)} announcements.")
        return announcements

from src.boards.board_source import BoardSource
import logging

class CEBoard(BoardSource):
    def __init__(self):
        super().__init__(
            base_url="https://www.hanbat.ac.kr/prog/bbsArticle/BBSMSTR_000000000333/list.do",
            table_class="board_list table table-default",
            pagination_class="pagination"
        )

    def fetch_announcements(self):
        """
        CEBoard는 BoardSource의 기본 fetch_announcements 메서드를 사용하여
        데이터를 가져오고 로깅을 처리합니다.
        """
        announcements = super().fetch_announcements()
        if not announcements:
            logging.warning("CEBoard: No announcements found.")
        else:
            logging.info(f"CEBoard fetched {len(announcements)} announcements.")
        return announcements

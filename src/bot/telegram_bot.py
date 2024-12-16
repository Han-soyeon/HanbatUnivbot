import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext
from telegram import Update
from datetime import datetime, timedelta
from src.handlers.board_handler import BoardHandler
from src.handlers.report_handler import ReportHandler
import logging
import time

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment.")
        self.app = ApplicationBuilder().token(self.token).build()
        self.board_handler = BoardHandler()
        
        # 캐시 설정
        self.cache = {}
        self.cache_last_updated = {}
        self.cache_ttl = 1800  # 캐시 유효 시간 (초) - 30분
        
        # ReportHandler 초기화 시 캐시를 전달
        self.report_handler = ReportHandler(cached_data=self.cache)

        self._register_handlers()

    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", self._start))
        self.app.add_handler(CommandHandler("board", self._board))
        self.app.add_handler(CommandHandler("report", self._report))

    def _filter_recent_announcements(self, announcements):
        filtered = []
        one_month_ago = datetime.now() - timedelta(days=30)
        for announcement in announcements:
            try:
                date_str = announcement[4]
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                if date_obj >= one_month_ago:
                    filtered.append(announcement)
            except ValueError:
                logging.warning(f"Skipping malformed date: {announcement[4]}")
        return filtered

    def _format_announcements(self, announcements):
        formatted = []
        for announcement in announcements:
            formatted.append(
                f"번호: {announcement[0]}\n"
                f"제목: {announcement[1]}\n"
                f"작성자: {announcement[2]}\n"
                f"조회수: {announcement[3]}\n"
                f"등록일: {announcement[4]}\n{'-' * 30}"
            )
        return "\n".join(formatted)

    def _is_cache_valid(self, department):
        if department not in self.cache_last_updated:
            return False
        is_valid = (time.time() - self.cache_last_updated[department]) < self.cache_ttl
        return is_valid and department in self.cache

    def _update_cache(self, department, data):
        try:
            if not isinstance(data, list) or not all(isinstance(row, list) and len(row) == 5 for row in data):
                raise ValueError(f"Invalid data format for cache: {data}")
            self.cache[department] = data
            self.cache_last_updated[department] = time.time()
            # ReportHandler의 캐시를 동기화
            self.report_handler.update_cache(department, data)
            logging.info(f"Cache updated for department: {department}, total items: {len(data)}")
        except Exception as e:
            logging.error(f"Error updating cache for department {department}: {e}")
            raise

    async def _start(self, update: Update, context: CallbackContext):
        logging.info("Start command received")
        await update.message.reply_text("Hanbat University Bot에 오신 것을 환영합니다!")

    async def _board(self, update: Update, context: CallbackContext):
        logging.info(f"Board command received with args: {context.args}")
        if len(context.args) > 0:
            department = context.args[0].lower()
            try:
                if self._is_cache_valid(department):
                    announcements = self.cache[department]
                else:
                    announcements = self.board_handler.handle_request(department)
                    if announcements:
                        self._update_cache(department, announcements)
                    else:
                        await update.message.reply_text("해당 학과에 대한 공지사항이 없습니다.")
                        return

                recent_announcements = self._filter_recent_announcements(announcements)
                if recent_announcements:
                    formatted_announcements = self._format_announcements(recent_announcements)
                    await update.message.reply_text(formatted_announcements)
                else:
                    await update.message.reply_text("최근 한 달간 등록된 공지사항이 없습니다.")
            except Exception as e:
                logging.error(f"Error in _board: {e}")
                await update.message.reply_text(f"오류 발생: {e}")
        else:
            await update.message.reply_text("사용법: /board [학과명] (예: /board computer)")

    async def _report(self, update: Update, context: CallbackContext):
        logging.info(f"Report command received with args: {context.args}")
        if len(context.args) >= 2:
            format = context.args[0].lower()
            department = context.args[1].lower()
            try:
                if not self._is_cache_valid(department):
                    raw_data = self.board_handler.handle_request(department)
                    if not raw_data:
                        await update.message.reply_text("해당 학과에 대한 데이터가 없습니다.")
                        return
                    self._update_cache(department, raw_data)

                result = self.report_handler.generate_report(format, department)
                await update.message.reply_text(result)
            except Exception as e:
                logging.error(f"Error in _report: {e}")
                await update.message.reply_text(f"오류 발생: {e}")
        else:
            await update.message.reply_text("사용법: /report [형식] [학과명] (예: /report excel computer)")

    def run(self):
        logging.info("Telegram Bot is starting...")
        self.app.run_polling()


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()

from src.boards.ce_board import CEBoard
from src.boards.ee_board import EEBoard
import logging

class BoardFactory:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def get_board(self, department: str):
        """
        Get the appropriate board instance based on the department name.
        :param department: Department name (e.g., "computer", "electrical").
        :return: An instance of the board class for the specified department.
        """
        try:
            # Validate department input
            if not isinstance(department, str) or not department.strip():
                logging.error("Department name must be a non-empty string.")
                raise ValueError("Department name must be a non-empty string.")

            # Normalize department name to lowercase
            normalized_department = department.strip().lower()
            logging.info(f"Getting board for department: '{normalized_department}'")

            if normalized_department == "computer":
                logging.info("Returning CEBoard instance.")
                return CEBoard()
            elif normalized_department == "electrical":
                logging.info("Returning EEBoard instance.")
                return EEBoard()
            else:
                logging.error(f"Unknown department: '{normalized_department}'")
                raise ValueError(f"Unknown department: '{normalized_department}'")
        except ValueError as ve:
            logging.error(f"ValueError: {ve}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error while getting board for {department}: {e}")
            raise

import logging
import os

class AnalysisLogger:
    def __init__(self):
        self.logger = logging.getLogger("analysis_logger")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_analysis(self, user_id: str, dataset_id: str, analysis_type: str):
        self.logger.info(f"User {user_id} performed {analysis_type} on dataset {dataset_id}")

    def log_error(self, message: str):
        self.logger.error(message)

analysis_logger = AnalysisLogger()

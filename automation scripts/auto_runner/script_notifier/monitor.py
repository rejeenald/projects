import logging
import os
import pandas as pd
import datetime as dt

try:
    from .settings import STATUS_LOG
except:
    from settings import STATUS_LOG

class ScriptStatusMonitor:
    def __init__(self, script_name:str, status:str) -> None:
        logging.info("============================ScriptErrorLogger============================")
        # logging.info(f"Error detected for script {script_name}")
        logging.info(f"Monitoring script {script_name}")
        self.status_df = self._create_dataframe(script_name=script_name, status=status)

    def _create_dataframe(self, script_name:str, status:str) -> pd.DataFrame:
        timestamp = dt.datetime.now()
        status_data = {"script": [script_name], "timestamp": [timestamp], "status": [status]}
        return pd.DataFrame(status_data)

    def save_to_log(self) -> None:
        logging.info("Saving to a logfile...")
        if self._is_file_exists():
            logging.info(f"Appending to monitor csv the status of the script {STATUS_LOG}.")
            self.status_df.to_csv(STATUS_LOG, mode="a", index=False, header=False)
        else:
            self.status_df.to_csv(STATUS_LOG, index=False)
        logging.info("Status information saved!")

    def _is_file_exists(self) -> bool:
        return os.path.isfile(STATUS_LOG)

# if __name__ == "__main__":
#     s = ScriptStatusMonitor("vcspapi", "fail")
#     s.save_to_log()

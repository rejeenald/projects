import datetime as dt
import logging
import os
from time import sleep
from artboard_processor import ArtboardProcessor
from settings import TO_PRINT_ARTBOARD, ACTIVATE_EMAIL_NOTIFICATION
from script_notifier.monitor import ScriptStatusMonitor
from script_notifier.status_reader import NotifyToEmail

if __name__ == "__main__":
    artboard_processor = ArtboardProcessor(to_print_artboard=TO_PRINT_ARTBOARD)

    try:
        artboard_processor.process_regular_artboard()
        status = "success"
    except Exception as e:
        logging.error(f"Failed to run successfully process regular artboard: {e}")
        status = "fail"

    monitor = ScriptStatusMonitor(script_name="regular artboard", status=status)
    monitor.save_to_log()
    sleep(5)

    if ACTIVATE_EMAIL_NOTIFICATION:
        NotifyToEmail()
        print("Done running custom updater auto runner.")
        logging.info("Done running custom updater auto runner.\n\n")
import logging
import pandas as pd
try:
    from .email_sender import EmailNotification
    from .settings import SUBJECT_FOR_FAILURE, SUBJECT_FOR_SUCCESS, STATUS_LOG, RECIPIENTS
except:
    from email_sender import EmailNotification
    from settings import SUBJECT_FOR_FAILURE, SUBJECT_FOR_SUCCESS, STATUS_LOG, RECIPIENTS


class NotifyToEmail:
    def __init__(self, to:list=RECIPIENTS) -> None: 
        self.notif = EmailNotification(to=to)
        return self._notify_to_email()

    def _notify_to_email(self) -> None:
        monitor = pd.read_csv(STATUS_LOG)
        if self._has_fails(monitor=monitor):
            subject=SUBJECT_FOR_FAILURE
        else:
            subject=SUBJECT_FOR_SUCCESS
            
        self.notif.send_notification(message=monitor.to_string(), subject=subject)

    def _has_fails(self, monitor:pd.DataFrame) -> list:
        status = monitor["status"].tolist()
        logging.info(f"Status: {status}")
        if "fail" in status:
            return True
        return False


if __name__ == "__main__":
    NotifyToEmail(to="it@smartish.com")
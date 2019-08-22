import hashlib
from datetime import datetime, timezone

from doc_manager import USAGE_DATA_CAPTURING
from doc_manager.db import get_db
from utils import events_name


class DataCaptureLogger(object):

    def __init__(self):
        self.db = get_db()

    def generate_psuedonymized_string(self, input_data):
        return str(int(hashlib.sha1(str(input_data).encode()).hexdigest(), 16) % (10 ** 8))

    def capture_data(self, event_key, *args, **kwargs):
        if USAGE_DATA_CAPTURING:
            datetime_now = datetime.now(timezone.utc).strftime("%m/%d/%Y - %I:%M:%S %p %Z")

            if event_key == events_name.FILE_UPLOAD_STARTED:
                self.db.usage_events.insert_one(
                    {
                        'timestamp': datetime_now,
                        'user': self.generate_psuedonymized_string(kwargs.get('user')),
                        'ip_address': self.generate_psuedonymized_string(kwargs.get('ip_address')),
                        'action': "File upload started",
                        'metadata': {
                            'fileName': kwargs.get('file_name'),
                            'fileSize': kwargs.get('file_size')
                        }
                    }
                )
            elif event_key == events_name.FILE_UPLOAD_FAILED:
                self.db.usage_events.insert_one(
                    {
                        'timestamp': datetime_now,
                        'user': self.generate_psuedonymized_string(kwargs.get('user')),
                        'ip_address': self.generate_psuedonymized_string(kwargs.get('ip_address')),
                        'action': "File upload failed",
                        'metadata': {
                            'fileName': kwargs.get('file_name'),
                            'fileSize': kwargs.get('file_size')
                        }
                    }
                )
            elif event_key == events_name.FILE_UPLOAD_COMPLETE:
                self.db.usage_events.insert_one(
                    {
                        'timestamp': datetime_now,
                        'user': self.generate_psuedonymized_string(kwargs.get('user')),
                        'ip_address': self.generate_psuedonymized_string(kwargs.get('ip_address')),
                        'action': "File upload complete",
                        'metadata': {
                            'fileName': kwargs.get('file_name'),
                            'fileSize': kwargs.get('file_size')
                        }
                    }
                )
            elif event_key == events_name.UPLOAD_WINDOW_STARTED:
                self.db.usage_events.insert_one(
                    {
                        'timestamp': datetime_now,
                        'user': self.generate_psuedonymized_string(kwargs.get('user')),
                        'ip_address': self.generate_psuedonymized_string(kwargs.get('ip_address')),
                        'action': "Upload Window Started",
                        'metadata': {}
                    }
                )
            elif event_key == events_name.UPLOAD_COMPLETE:
                self.db.usage_events.insert_one(
                    {
                        'timestamp': datetime_now,
                        'user': self.generate_psuedonymized_string(kwargs.get('user')),
                        'ip_address': self.generate_psuedonymized_string(kwargs.get('ip_address')),
                        'action': "Upload Complete",
                        'metadata': {
                            'fileName': kwargs.get('fileName'),
                            'pageNum': kwargs.get('pageNumber'),
                            'suspiciousChars': kwargs.get("suspiciousChars"),
                            'totalChars': kwargs.get("totalChars"),
                            'wordsFromDict': kwargs.get("wordsFromDict"),
                            'wordsTotal': kwargs.get("wordsTotal")
                        }
                    }
                )

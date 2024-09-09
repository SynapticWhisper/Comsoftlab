import imaplib
import email
from email.header import decode_header
import base64
# from bs4 import BeautifulSoup
import re
from typing import Optional

# mail_pass = "password mail"
# username = "username@mail.ru"
# imap_server = "imap.mail.ru"


def get_imap_session(username: str, password: str, imap_server: str) -> imaplib.IMAP4_SSL:
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(username, password)
    return imap

class IMAPService:
    def __init__(self, session=None):
        self.session = session or get_imap_session(username="username@mail.ru", password="password mail", imap_server="imap.mail.ru")

    def __get_messages_uids(self) -> list[bytes]:
        result, data = self.session.uid('search', None, "ALL")
        if result == 'OK':
            return data[0].split()
        return []

    def get_new_messages_from_uid(self, last_seen_message_uid: Optional[bytes]) -> list[bytes]:
        messages_uids = self.__get_messages_uids()
        start, stop = 0, len(messages_uids) - 1
        
        if last_seen_message_uid is None:
            return messages_uids
        
        while start <= stop:
            mid = (stop + start) // 2
            if messages_uids[mid] == last_seen_message_uid:
                return messages_uids[mid + 1:]
            elif messages_uids[mid] > last_seen_message_uid:
                stop = mid - 1
            else:
                start = mid + 1
        
        return []
    
    def get_messages(self, last_seen_message_uid: Optional[bytes]):
        for uid in self.get_new_messages_from_uid(last_seen_message_uid):
            res, msg = self.session.uid('fetch', uid, '(RFC822)')
            yield msg
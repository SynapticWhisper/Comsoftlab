import email
import imaplib
from email.message import Message
from enum import Enum
from typing import Optional

from .parse_message import date_parse, decode_message_part, get_attachments, get_letter_text

# mail_pass = "password mail"
# username = "username@mail.ru"
# imap_server = "imap.mail.ru"

class Servers(str, Enum):
    YANDEX: str = "imap.yandex.ru"
    MAIL: str = "imap.mail.ru"
    GMAIL: str = "imap.gmail.com"


def get_imap_session(username: str, password: str, imap_server: Servers) -> imaplib.IMAP4_SSL:
    imap = imaplib.IMAP4_SSL(imap_server)
    login_status, _ = imap.login(username, password)
    selection_status, _ = imap.select()
    if login_status == "OK" and selection_status == "OK":
        return imap
    else:
        raise Exception # Поменять на HTTPException кричать что не правильный логин или пароль или что-то там


class IMAPService:
    def __init__(self, username: str, password: str, imap_server: Servers = Servers.MAIL):
        self.__session = get_imap_session(
            username=username,
            password=password,
            imap_server=imap_server.value
        )

    def __get_messages_uids(self) -> list[bytes]:
        result, data = self.__session.uid('search', None, "ALL")
        if result == 'OK':
            return data[0].split()
        return []

    def __get_new_messages_from_uid(self, last_seen_message_uid: Optional[bytes]) -> list[bytes]:
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
    
    def __message_to_dict(msg_uid: bytes, msg: list[tuple[bytes], bytes]) -> dict[str, str]:
        msg: Message = email.message_from_bytes(msg[0][1])

        message: dict[str, str] = {
            "message_uid": msg_uid,
            "from_user": decode_message_part(msg["From"]),
            "theme": decode_message_part(msg["Subject"]),
            "delivery_date": date_parse(email.utils.parsedate_tz(msg["Date"])),
            "message_text": get_letter_text(msg),
            "attachments": get_attachments(msg)
        }

        return message

    
    def get_messages(self, last_seen_message_uid: Optional[bytes]):
        for uid in self.__get_new_messages_from_uid(last_seen_message_uid):
            res, msg = self.__session.uid('fetch', uid, '(RFC822)')
            if res == "OK":
                yield self.__message_to_dict(uid, msg)
            else:
                yield
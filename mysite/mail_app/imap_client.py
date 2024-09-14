import email
from http.client import HTTPException
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


def get_imap_session(email: str, password: str, imap_server: Servers) -> imaplib.IMAP4_SSL:
    imap = imaplib.IMAP4_SSL(imap_server)
    login_status, _ = imap.login(email, password)
    selection_status, _ = imap.select()
    if login_status == "OK" and selection_status == "OK":
        return imap
    else:
        raise HTTPException


class IMAPService:
    def __init__(self, email: str, password: str, imap_server: Servers = Servers.MAIL):
        self.__session = get_imap_session(
            email=email,
            password=password,
            imap_server=imap_server
        )

    def get_messages_uids(self) -> list[bytes]:
        result, data = self.__session.uid('search', None, "ALL")
        if result == 'OK':
            return data[0].split()
        return []
    
    @staticmethod
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

    
    def get_messages(self, new_messages_uids: list[bytes]):
        for uid in new_messages_uids:
            res, msg = self.__session.uid('fetch', uid, '(RFC822)')
            print(uid, msg)
            if res == "OK":
                yield self.__message_to_dict(msg_uid=uid, msg=msg)
            else:
                yield

    def close_session(self):
        self.__session.close()
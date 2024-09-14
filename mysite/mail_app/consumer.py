import json
from typing import Optional
from channels.generic.websocket import WebsocketConsumer
from .imap_client import IMAPService
from .models import Message, User

class MailConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'

        self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        self.user = User.objects.get(pk=self.user_id)
        self.imap_service = IMAPService(self.user.email, self.user.password, self.user.imap_server)

        self.accept()


    def __get_new_messages_from_uid(self, last_seen_message_uid: Optional[bytes]) -> list[bytes]:
        messages_uids = self.imap_service.get_messages_uids()
        start, stop = 0, len(messages_uids) - 1

        total_checked = 0

        self.send(text_data=json.dumps({
            'status': 'reading',
            'total_messages': len(messages_uids),
            'messages_checked': total_checked,
        }))

        if last_seen_message_uid is None:
            return messages_uids
        
        while start <= stop:
            mid = (stop + start) // 2
            if messages_uids[mid] == last_seen_message_uid:
                return messages_uids[mid + 1:]
            elif messages_uids[mid] > last_seen_message_uid:
                total_checked += (mid - start + 1)
                stop = mid - 1
            else:
                total_checked += (mid - start + 1)
                start = mid + 1
            
            self.send(text_data=json.dumps({
                'status': 'reading',
                'total_messages': len(messages_uids),
                'messages_checked': total_checked,
            }))
        
        return []

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('message') != 'GET_MESSAGES':
                return
            
            last_message: Message = Message.objects.filter(user=self.user.id).order_by("-delivery_date").first()
            last_message_uid = last_message.message_uid.tobytes() if last_message else None
            new_messages_uids = self.__get_new_messages_from_uid(last_message_uid)
            message_batch = []
            sent_messages = 0

            for message in self.imap_service.get_messages(new_messages_uids):
                self.send(text_data=json.dumps({
                    'status': 'sending',
                    'total_messages': len(new_messages_uids),
                    'sent_messages': sent_messages,
                    'message': {
                        'message_uid': message["message_uid"].decode('utf-8'),
                        'from_user': message["from_user"],
                        'theme': message["theme"],
                        'delivery_date': message["delivery_date"].strftime('%d %b %Y %H:%M:%S'),
                        'message_text': message["message_text"],
                        'attachments': message["attachments"]
                    }
                }))
                
                message_batch.append(message)
                
                if len(message_batch) == 50:
                    self._save_messages_batch(message_batch)
                    message_batch = []

                sent_messages += 1
            
            if message_batch:
                self._save_messages_batch(message_batch)

            self.send(text_data=json.dumps({
                'status': 'complete',
                'total_messages': len(new_messages_uids),
                'sent_messages': sent_messages,
            }))
        except Exception as e:
            self.send(text_data=json.dumps({
                'status': 'error',
                'message': str(e),
            }))

    def _save_messages_batch(self, message_batch):
        Message.objects.bulk_create([
            Message(
                message_uid=msg["message_uid"],
                from_user=msg["from_user"],
                theme=msg["theme"],
                delivery_date=msg["delivery_date"],
                message_text=msg["message_text"],
                attachments=msg["attachments"],
                user=self.user,
            )
            for msg in message_batch
        ])

    def disconnect(self, close_code):
        if hasattr(self, 'imap_service'):
            self.imap_service.close_session()
        super().disconnect(close_code)

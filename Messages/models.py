from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


User = get_user_model()
# Create your models here.


class Messages(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    ist_timestamp = models.DateTimeField(null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Receiver")
    message = models.CharField(max_length=800)

@receiver(post_save, sender=Messages)
def appointment_changes(sender, instance, **kwargs):
    try:
        info_data = {
            "notification_type": "message",
            "sender_id": instance.sender.id,
            "receiver_id": instance.receiver.id,
            "message_id": instance.id,
            "click_action" : "message_screen",
        }

        print("Simulated push notification details:")
        print("Notification type:", info_data["notification_type"])
        print("Sender ID:", info_data["sender_id"])
        print("Receiver ID:", info_data["receiver_id"])
        print("Message ID:", info_data["message_id"])

        # Get the receiver's FCM token directly from the User model
        receiver = instance.receiver
        print("Receiver FCM Token:", receiver.fcm_token)  # Debug output

        fcm_token = receiver.fcm_token
        if fcm_token:
            print("Found FCM Token:", fcm_token)  # Debug output
            print("New Message:")
            print("Sender:", instance.sender.firstname)
            print("Receiver:", receiver.firstname)
            print("Message:", instance.message)
            send_notification(
                [fcm_token],
                'A new message received',
                f'You received a new message from {(instance.sender.firstname).capitalize()}',
                action="message_screen",
                info_data=info_data,


            )

    except Exception as e:
        print("Exception:", e)


        
##below code is before july
# @receiver(post_save, sender=Messages)
# def appointment_changes(sender, instance, **kwargs):
#     try:
#         info_data = {
#             "notification_type" : "message",
#             "sender_id" : instance.sender.id ,
#             "receiver_id" : instance.receiver.id,
#             "message_id" : instance.id,
#         }

#         fcm_tokens = instance.receiver.fcm_tokens.all()
#         if fcm_tokens.exists():
#             fcm_token = [f.fcm_token for f in fcm_tokens]
#             print(fcm_token)
#             send_notification(
#                 fcm_token,
#                 'A new message recieved',
#                 f'You received  a new message from {(instance.sender.firstname).capitalize()}',
#                 action = "messages",
#                 info_data = info_data
#             )

#     except Exception as e:
#         print(e)
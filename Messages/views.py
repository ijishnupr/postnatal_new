from os import stat
from Accounts.models import CustomerDetails, DoctorDetails,SalesTeamDetails,ConsultantInfo
from .models import *
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
User = get_user_model()
from django.db.models import Max

from django.utils import timezone
from datetime import timedelta
import pytz
from datetime import datetime
import datetime

# Create your views here.


from datetime import timedelta

@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def send_message(request):
    user = request.user
    if not user.role == User.ADMIN and not user.role == User.HOSPITAL_MANAGER:
        data = request.data.copy()
        data['sender'] = user
        receiver = request.data.get('receiver', None)
        message = request.data.get('message', None)
        try:
            receiver = User.objects.get(id=receiver)
        except User.DoesNotExist:
            return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)
        if message is not None:
            stripSpaces = message.replace(" ", '')
            if len(stripSpaces) != 0:
                ist = pytz.timezone('Asia/Kolkata')
                message_instance = Messages(sender=user, receiver=receiver, message=message)
                message_instance.save()

                # Calculate IST timestamp
                ist_timestamp = timezone.localtime(message_instance.timestamp, ist)
                ist_timestamp_with_offset = ist_timestamp + datetime.timedelta(hours=5, minutes=30)
                message_instance.ist_timestamp = ist_timestamp_with_offset
                message_instance.save()

                return Response({'success': 'Message sent'})
        return Response({'error': 'Empty message'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_all_messages(request):
    user = request.user
    if not user.role == User.ADMIN and not user.role == User.HOSPITAL_MANAGER:
        receiverDetails = {}
        receiver_id = request.query_params.get('receiver', None)
        if receiver_id is not None:
            try:
                receiver = User.objects.get(id=receiver_id, is_active=True)
                receiverDetails['id'] = receiver.id
                receiverDetails['image_url'] = "https://" + str(get_current_site(request)) + "/media/" + str(
                    receiver.profile_img)
                receiverDetails[
                    'name'] = receiver.firstname + " " + receiver.lastname if receiver.lastname is not None else receiver.firstname
                if receiver.role == User.DOCTOR:
                    details = receiver.docDetails.first()
                    receiverDetails['speciality'] = details.speciality
                receiverDetails['joining_date'] = receiver.dateJoined.strftime('%Y-%m-%d %I:%M:%S %p')
            except User.DoesNotExist:
                return Response({'error': 'Receiver not found'}, status=status.HTTP_404_NOT_FOUND)

            # Fetch messages and annotate with the latest timestamp
            messages = Messages.objects.filter(
                Q(sender=user.id) | Q(sender=receiver.id), Q(receiver=user.id) | Q(receiver=receiver.id)
            ).prefetch_related('receiver', 'sender')

            messages = messages.annotate(latest_timestamp=Max('timestamp'))

            # Sort messages by the latest timestamp in ascending order to reverse them
            messages = messages.order_by('latest_timestamp')

            ist = pytz.timezone('Asia/Kolkata')
            for message in messages:
                message.timestamp = message.latest_timestamp.astimezone(ist)

            # Serialize messages
            serializer = AllMessageSerializer(messages, many=True)

            try:
                last_message = messages.latest('latest_timestamp')
                formatted_ist_time = last_message.latest_timestamp.astimezone(ist).strftime('%Y-%m-%d %I:%M:%S %p') if last_message.latest_timestamp else None
                receiverDetails['last_message_time'] = formatted_ist_time
            except Messages.DoesNotExist:
                receiverDetails['last_message_time'] = None

            response_data = {
                'messages': serializer.data,
                'receiverDetails': receiverDetails,
            }

            return Response(response_data)
        else:
            return Response({"error": "Receiver empty"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_all_consultants(request):
    user = request.user
    consultants_id = []
    id = user.id
    msgs = Messages.objects.filter(Q(sender=id) | Q(receiver=id)).prefetch_related('sender', 'receiver').distinct(
        'sender', 'receiver')
    for msg in msgs:
        if msg.sender.role == User.CONSULTANT:
            consultants_id.append(msg.sender.id)
        else:
            consultants_id.append(msg.receiver.id)

    recent_consultants = User.objects.filter(role=User.CONSULTANT, id__in=consultants_id, is_active=True)
    remaining_consultants = User.objects.filter(role=User.CONSULTANT, is_active=True).exclude(id__in=consultants_id)

    recent = AllUserSerializer(recent_consultants, many=True, context={'request': request})
    remaining = AllUserSerializer(remaining_consultants, many=True, context={'request': request})

    current_time = timezone.now()

    recent_consultants_info = []
    remaining_consultants_info = []

    for consultant_info in recent.data:
        consultant_id = consultant_info['id']
        try:
            consultant = User.objects.get(id=consultant_id, is_active=True)
        except User.DoesNotExist:
            continue

        serialized_consultant = AllUserSerializer(consultant, context={'request': request}).data

        # Retrieve ist_timestamp from Messages model
        last_message = Messages.objects.filter(
            Q(sender=user, receiver=consultant) | Q(sender=consultant, receiver=user)
        ).latest('timestamp')

        ist_time = last_message.ist_timestamp
        formatted_ist_time = ist_time.strftime('%Y-%m-%d %I:%M:%S %p') if ist_time else None
        serialized_consultant["last_message_time"] = formatted_ist_time

        recent_consultants_info.append(serialized_consultant)

    for consultant_info in remaining.data:
        consultant_id = consultant_info['id']
        try:
            consultant = User.objects.get(id=consultant_id, is_active=True)
        except User.DoesNotExist:
            continue

        serialized_consultant = AllUserSerializer(consultant, context={'request': request}).data

        # Include joining date
        joining_date = consultant.dateJoined.strftime('%Y-%m-%d') if consultant.dateJoined else None
        serialized_consultant["joining_date"] = joining_date

        remaining_consultants_info.append(serialized_consultant)

    return Response({'recentChats': recent_consultants_info, 'remainingChats': remaining_consultants_info})



@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_clients_doctor(request):
    user = request.user

    if user.role == User.CLIENT:
        try:
            details = user.customer_details.first()
            if details.referalId:
                doctor = details.referalId
            else:
                return JsonResponse({'error': 'doctor not found'}, status=status.HTTP_404_NOT_FOUND)
        except CustomerDetails.DoesNotExist:
            return JsonResponse({'error': 'Customer details not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get last message between client and doctor
        last_message = Messages.objects.filter(
            Q(sender=user, receiver=doctor.user) | Q(sender=doctor.user, receiver=user)
        ).latest('timestamp')

        ist_time = last_message.ist_timestamp
        formatted_ist_time = ist_time.strftime('%Y-%m-%d %I:%M:%S %p') if ist_time else None

        firstname = doctor.user.firstname
        lastname = doctor.user.lastname
        id = doctor.user.id
        speciality = doctor.speciality
        image_url = "https://" + str(get_current_site(request)) + "/media/" + str(doctor.user.profile_img)

        return JsonResponse({
            'id': id,
            'firstname': firstname,
            'lastname': lastname,
            'speciality': speciality,
            'image_url': image_url,
            'last_message_time': formatted_ist_time  # Include IST time of last message
        })
    else:
        return Response({'error': "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def get_all_sales(request):
    user = request.user
    sales_id = []
    id = user.id
    msgs = Messages.objects.filter(Q(sender=id) | Q(receiver=id)).prefetch_related('sender', 'receiver').distinct(
        'sender', 'receiver')

    for msg in msgs:
        if msg.sender.role == User.SALES:
            sales_id.append(msg.sender.id)
        else:
            sales_id.append(msg.receiver.id)

    recent_sales = User.objects.filter(role=User.SALES, id__in=sales_id, is_active=True).prefetch_related('salesDetails')
    remaining_sales = User.objects.filter(role=User.SALES, is_active=True).exclude(id__in=sales_id).prefetch_related(
        'salesDetails')

    recent = AllUserSerializer(recent_sales, many=True, context={'request': request})
    remaining = AllUserSerializer(remaining_sales, many=True, context={'request': request})

    current_time = timezone.now()

    recent_sales_info = []
    remaining_sales_info = []

    for sales_info in recent.data:
        sales_id = sales_info['id']
        try:
            sales = User.objects.get(id=sales_id, is_active=True)
        except User.DoesNotExist:
            continue

        serialized_sales = AllUserSerializer(sales, context={'request': request}).data

        # Retrieve ist_timestamp from Messages model
        last_message = Messages.objects.filter(
            Q(sender=user, receiver=sales) | Q(sender=sales, receiver=user)
        ).latest('timestamp')

        ist_time = last_message.ist_timestamp
        formatted_ist_time = ist_time.strftime('%Y-%m-%d %I:%M:%S %p') if ist_time else None
        serialized_sales["last_message_time"] = formatted_ist_time

        recent_sales_info.append(serialized_sales)

    for sales_info in remaining.data:
        sales_id = sales_info['id']
        try:
            sales = User.objects.get(id=sales_id, is_active=True)
        except User.DoesNotExist:
            continue

        serialized_sales = AllUserSerializer(sales, context={'request': request}).data

        # Include joining date
        joining_date = sales.dateJoined.strftime('%Y-%m-%d') if sales.dateJoined else None
        serialized_sales["joining_date"] = joining_date

        remaining_sales_info.append(serialized_sales)

    return Response({'recentChats': recent_sales_info, 'remainingChats': remaining_sales_info})



@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_all_clients(request):
    user = request.user
    clients = CustomerDetails.objects.all().prefetch_related("user")
    serializer = AllClientSerializer(clients, many=True, context={'request' : request})
    return JsonResponse(serializer.data, safe=False)




import datetime



@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def get_all_clients_of_doctor(request):
    user = request.user
    if user.role == User.DOCTOR:
        id = user.id
        clients_id = []
        try:
            details = user.docDetails.first()
        except DoctorDetails.DoesNotExist:
            return JsonResponse({"error": "doctor not found"}, status=status.HTTP_404_NOT_FOUND)

        current_time = timezone.now()  # Get the current time in the desired timezone

        client_messages = (
            Messages.objects.filter(
                Q(sender=id) | Q(receiver=id)
            )
            .values('sender', 'receiver')
            .annotate(
                last_message_time=Max('timestamp')
            )  # Retrieve the latest message time
        )

        recent_clients_id = set()
        recent_clients_info = []
        remaining_clients_info = []

        for msg_info in client_messages:
            sender_id = msg_info['sender']
            receiver_id = msg_info['receiver']
            client_id = sender_id if sender_id != id else receiver_id

            try:
                client = User.objects.get(id=client_id, is_active=True)
            except User.DoesNotExist:
                continue

            serialized_client = AllUserSerializer(client, context={'request': request}).data

            last_message_time = msg_info['last_message_time']
            if last_message_time:
                if not isinstance(last_message_time, datetime.datetime):
                    last_message_time = datetime.datetime.strptime(last_message_time, '%Y-%m-%d %I:%M:%S %p')
                ist_time = last_message_time + timedelta(hours=5, minutes=30)  # Add the offset to get IST time
                formatted_ist_time = ist_time.strftime('%Y-%m-%d %I:%M:%S %p')
                serialized_client["last_message_time"] = formatted_ist_time
            else:
                formatted_ist_time = None

            if client_id not in recent_clients_id:
                recent_clients_info.append(serialized_client)
                recent_clients_id.add(client_id)
            else:
                # Update the latest message time if this is the same client
                for client_info in recent_clients_info:
                    if client_info['id'] == client_id:
                        client_info['last_message_time'] = formatted_ist_time

        remaining_clients = User.objects.filter(
            role=User.CLIENT, customer_details__referalId=details.id, is_active=True
        ).exclude(id__in=clients_id)

        for client_info in remaining_clients:
            client_id = client_info.id
            try:
                client = User.objects.get(id=client_id, is_active=True)
            except User.DoesNotExist:
                continue

            serialized_client = AllUserSerializer(client, context={'request': request}).data

            joining_date = client.dateJoined.strftime('%Y-%m-%d') if client.dateJoined else None
            serialized_client["joining_date"] = joining_date

            remaining_clients_info.append(serialized_client)

        return Response({'recentChats': recent_clients_info, 'remainingChats': remaining_clients_info})
    else:
        return JsonResponse({'error': "unauthorized request"}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def generate_message_notification(request, user_id, user_pic):
   
    click_action = "message_screen"
    notification_data = {
        "click_action": click_action,
        "user_id": user_id,
        "user_pic": user_pic,
    }
    return JsonResponse(notification_data)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def all_sales_team(request):
    try:
        user = request.user
        user_id = request.query_params.get('user_id', None)
        sales = SalesTeamDetails.objects.filter(user__isnull=False, user__role=User.SALES).prefetch_related('user')

        serializer = SalesTeamSerializer(sales, many=True, context={'request': request})

        serialized_data = serializer.data

        if user_id and str(user_id) == str(user.id):  # Check if user id matches the requested user_id
            for data in serialized_data:
                data['custom_date'] = data.pop('dateJoined')  # Rename 'dateJoined' to 'custom_date'

        context = {
            'count': len(serialized_data),
            'details': serialized_data
        }

        return JsonResponse(context)
    except Exception as e:
        print(e)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_consultants_list(request):
    user = request.user
    consultants = ConsultantInfo.objects.filter(user__role=5).prefetch_related('user')

    serializer = ConsultantInfoWithCustomDateSerializer(consultants, many=True, context={'request': request})

    context = {
        'count': consultants.count(),
        'details': serializer.data
    }

    return JsonResponse(context, safe=False)

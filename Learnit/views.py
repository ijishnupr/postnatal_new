
from os import stat
from .serializers import *
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
# from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework_api_key.permissions import HasAPIKey
from Accounts.models import CustomerDetails
from django.contrib.auth import get_user_model

User = get_user_model()
from datetime import date

@api_view(['POST'])
def add_module(request):
    module=request.data.get('module')
    data=Modules.objects.create(name=module)
    return JsonResponse(status=200)

# Admin and sales adding videos
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_videos(request):
    user = request.user
    if user:
        is_update = False
        data = request.data.copy()
        moduleName = data.get('module', None)
        

        if moduleName is not None:
            try:
                module = Modules.objects.get(name__iexact=moduleName)
            except Modules.DoesNotExist:
                return JsonResponse({"error" : "Module not found"}, status=status.HTTP_404_NOT_FOUND)
    
        else:
            return JsonResponse({"error" : "module fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        data['module'] = module.id

        # check if video update
        try:
            vdo = Videos.objects.get( module=module.id)
            is_update = True
        except Videos.DoesNotExist:
            is_update = False

        if is_update == True:
            serializer = AddVideoSerializers(vdo, data=data)
        else:
            serializer = AddVideoSerializers(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse({"success" : "Successfull", "Data" : serializer.data})
        else:
            raise serializers.ValidationError({"error" : serializer.errors})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def get_module_data(request):
    customer = request.user
    if customer:
        module = request.query_params.get('module', None)
        # get selected module
        try:
            module = Modules.objects.get(name__iexact=module)
        except Modules.DoesNotExist:
            return JsonResponse({"error" : "selected module not found !"}, status=status.HTTP_404_NOT_FOUND)

     

        
        notes = Notes.objects.filter(customer=customer, module=module.id).first()
        video = Videos.objects.filter(module=module.id).first()

        videoserializer = AddVideoSerializers(video)
        noteserializer = NoteSerializer(notes)

        return JsonResponse({
            "video" : videoserializer.data,
            "note" : noteserializer.data,
         
        })
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)



# Add Notes
@api_view(['POST',])
@permission_classes((IsAuthenticated,))
def add_notes(request):
    user = request.user
    if user.role == User.CLIENT:
    # is_update = False
        data = request.data.copy()
        module = request.data.get('module', None)
        customer = user.id
        if module and customer is not None:
            try:
                customerDetails = user.customer_details.first()
            except :
                return JsonResponse({"Error" : "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                module = Modules.objects.get(name__iexact=module)
            except Modules.DoesNotExist:
                return JsonResponse({"error" : "Specified module not found"}, status=status.HTTP_404_NOT_FOUND)


            data['module'] = module.id
            
            data['customer'] = customer
            # check if notes update
            try:
                note = Notes.objects.get(customer=customer, module=module.id)
                serializer = NoteSerializer(note, data=data)
            except Notes.DoesNotExist:
                serializer = NoteSerializer(data=data)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({"success" : "notes added", "data" : serializer.data})
            else:
                raise serializers.ValidationError({"error" : serializer.errors})
        else:
            return JsonResponse({"error" : "module field cannot be empty"})
    else:
        return JsonResponse({'error' : 'unauthorized request'}, status=status.HTTP_401_UNAUTHORIZED)
import json
import requests
from django.http import JsonResponse, HttpResponse
from django_q.tasks import async_task
from rest_framework import generics, status
from rest_framework.views import APIView

from DocSet.models import DocSet
from DocSet.views import docset_name_cat
from djangoProject.settings import LLM_URL
from .models import Chat
from .serializers import ChatSerializer


def chat_create_task(name, docset_name):
    url = f'{LLM_URL}/chats/'
    js = {"name": name, "document_set_name": docset_name}
    res = requests.post(url, json=js)
    print(res)


def chat_delete_task(chat_id):
    url = f'{LLM_URL}/chats/{chat_id}'
    res = requests.delete(url)
    print(res)


class ChatCreateAPIView(generics.CreateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def post(self, request, *args, **kwargs):
        name = request.data.get('name')
        docSet_id = request.data.get('docSet')
        type = request.data.get('type')
        if Chat.objects.filter(name=name, docSet_id=docSet_id, type=type).exists():
            return JsonResponse({'error': 'Chat name already exists'}, status=status.HTTP_409_CONFLICT)
        elif DocSet.objects.filter(id=docSet_id).first() is None:
            return JsonResponse({'error': 'DocSet does not exist'}, status=status.HTTP_404_NOT_FOUND)
        chat = Chat.objects.create(name=name, docSet_id=docSet_id, type=type)
        async_task(chat_create_task, name, docset_name_cat(docSet_id, type))
        return JsonResponse({'success': 'Create success', 'chat_id': chat.id}, status=status.HTTP_201_CREATED)


class ChatListAPIView(generics.ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get(self, request, *args, **kwargs):
        docSet_id = self.request.query_params.get('docset')
        if DocSet.objects.filter(id=docSet_id).first() is None:
            return JsonResponse({'error': 'DocSet does not exist'}, status=status.HTTP_404_NOT_FOUND)
        queryset = Chat.objects.filter(docSet_id=docSet_id).all()
        serializer = ChatSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


class ChatRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get(self, request, **kwargs):
        chat = Chat.objects.get(pk=self.request.query_params.get('chat'))
        return JsonResponse({'ChatHistory': chat.getHistory()}, status=status.HTTP_200_OK)


class ChatChatAPIView(APIView):
    def post(self, request, **kwargs):
        chat_id = self.request.query_params.get('chat')
        content = request.data['content']
        chat = Chat.objects.get(pk=chat_id)
        user_content = {
            "isLlm": False,
            "content": content
        }
        chat.updateHistory(user_content)
        url = f'{LLM_URL}/chats/{chat_id}/'
        response = requests.post(url, json={"content": content})
        if response.status_code != 200:
            data = "大模型服务异常，请稍后再试"
            num = 0
            source = []
        else:
            data = response.json()['message']['content']
            num = len(response.json()['documents'])
            source = response.json()['documents']
        ai_content = {
            "isLlm": True,
            "content": data,
            "ifshowSource": True,
            "sourceNum": num,
            "sourceList": source
        }
        chat.updateHistory(ai_content)
        return JsonResponse(ai_content, status=status.HTTP_200_OK)


class ChatDestroyAPIView(generics.DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def destroy(self, request, *args, **kwargs):
        chat_id = self.request.query_params.get('chat')
        try:
            instance = self.get_queryset().get(pk=chat_id)
        except Chat.DoesNotExist:
            return JsonResponse({'error': 'Chat does not exist'}, status=status.HTTP_404_NOT_FOUND)
        self.perform_destroy(instance)
        async_task(chat_delete_task, chat_id)
        return JsonResponse({'success': 'Delete success'}, status=status.HTTP_204_NO_CONTENT)


class ExportRepairOrder(APIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def post(self, request, **kwargs):
        chat_id = self.request.query_params.get('chat')
        chat = Chat.objects.get(pk=chat_id)
        user_content = {
            "isLlm": False,
            "content": "生成维修记录单"
        }
        chat.updateHistory(user_content)
        url = f'{LLM_URL}/chats/{chat_id}/'
        response = requests.post(url, json={"content": "生成维修记录单"})
        num = 0
        source = []
        if response.status_code != 200:
            data = "大模型服务异常，请稍后再试"
        else:
            data = response.json()['message']['content']
        ai_content = {
            "isLlm": True,
            "content": data,
            "ifshowSource": True,
            "sourceNum": num,
            "sourceList": source
        }
        chat.updateHistory(ai_content)
        with open('维修记录单.txt', 'w') as f:
            json.dump(data, f)
        with open('维修记录单.txt', 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="维修记录单.txt"'
            return response

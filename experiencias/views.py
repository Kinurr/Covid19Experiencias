from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils import timezone
from django.urls import reverse
from .models import UserPost, UserComment
import csv
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
import time


def index(request):
    if request.method == 'POST':
        if request.POST['selected_type'] == "date":
            user_post_list = UserPost.objects.order_by('-pub_data')[:60]
        if request.POST['selected_type'] == "votes":
            user_post_list = UserPost.objects.order_by('-score')[:60]
    else:
        user_post_list = UserPost.objects.order_by('-score')[:60]
    context = {'user_post_list': user_post_list}
    return render(request, 'index.html', context)


def showAll(request):
    user_post_list = UserPost.objects.order_by('-pub_data')
    context = {'user_post_list': user_post_list}
    return render(request, 'index.html', context)


def userpost(request, user_post_id):
    user_post = get_object_or_404(UserPost, pk=user_post_id)
    context = {'user_post': user_post}
    return render(request, 'userpost.html', context)


# Register logic
# def register(request):
#    return render(request, 'register.html')

def register(request, context=None):
    if context is None:
        msg = 'Efetue Login'
    else:
        msg = context.message
    return render(request, 'register.html', {'message': msg})


def registeruser(request):
    user_name = request.POST['user_name']
    user_email = request.POST['email']
    user_pass = request.POST['password']
    check_user = User.objects.filter(username=user_name)
    print(check_user)
    ##############################################################################################################
    check_mail = User.objects.filter(email=user_email)
    if check_user is None and len(check_mail) == 0:
        user = User.objects.create_user(user_name, user_email, user_pass)
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse('experiencias:index'))
    else:
        if check_user is not None:
            msg = "Erro: UserName já atribuído"
        if len(check_mail) > 0:
            msg = "Erro: e-mail já atribuído"
        context = {'msg': msg}
        return render(request, 'register.html', context)


# Session logic
def userlogin(request, context=None):
    if context is None:
        msg = 'Efetue Login'
    else:
        msg = context.message
    return render(request, 'login.html', {'message': msg})


def loginuser(request):
    user_name = request.POST['user_name']
    user_pass = request.POST['password']
    user = authenticate(username=user_name,
                        password=user_pass)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse('experiencias:index'))
    else:
        msg = "Erro: credenciais inválidas"
        context = {'msg': msg}
        return render(request, 'login.html', context)


def logoutuser(request):
    logout(request)
    return HttpResponseRedirect(reverse('experiencias:index'))


# Post logic
def makepost(request):
    return render(request, 'makepost.html')


def createpost(request):
    post_title = request.POST['title']
    post_text = request.POST['text']
    post_img = request.POST['img']
    # Restrict to authenticated users
    if not request.user.is_authenticated:
        return HttpResponse('<h1>Não estás logado...</h1>')
    # post create in db
    user_post = UserPost(text=post_text, title=post_title, pub_data=timezone.now(), score=0,
                         user_name=request.user.username, img=post_img)
    user_post.save()
    return HttpResponseRedirect(reverse('experiencias:index'))


def editpost(request, user_post_id):
    user_post = UserPost.objects.get(id=user_post_id)
    context = {'user_post': user_post}
    return render(request, 'editpost.html', context)


def editLogicPost(request, user_post_id):
    post_title = request.POST['title']
    post_text = request.POST['text']
    post_img = request.POST['img']
    # Restrict to authenticated users
    if not request.user.is_authenticated:
        return HttpResponse('<h1>Não estás logado...</h1>')
    user_post = UserPost.objects.get(id=user_post_id)
    user_post.text = post_text
    user_post.title = post_title
    user_post.img = post_img
    user_post.save()
    return HttpResponseRedirect('/experiencias/' + str(user_post.id))


def deletepost(request, user_post_id):
    time.sleep(1)
    user_post = UserPost.objects.get(id=user_post_id)
    # Restrict either superuser or post author
    if request.user.is_superuser or request.user.username is user_post.user_name:
        user_post.delete()
        return HttpResponseRedirect(reverse('experiencias:index'))
    else:
        msg = 'Não tem permissões para essa acção!'
        return render(request, 'login.html', {'msg': msg})


# Comment making logic
def createcomment(request, user_post_id):
    # Restrict to authenticated users
    if not request.user.is_authenticated:
        msg = 'É necessário o Login para fazer comentários!'
        return render(request, 'login.html', {'msg': msg})
    comment_text = request.POST['comment_text']
    user_post = UserPost.objects.get(id=user_post_id)
    # Comment create in db
    user_post.usercomment_set.create(user_name=request.user.username, text=comment_text, pub_data=timezone.now())
    user_post.save()
    return HttpResponseRedirect('/experiencias/' + str(user_post.id))


def deletecomment(request, user_comment_id):
    time.sleep(1)
    user_comment = UserComment.objects.get(id=user_comment_id)
    user_post_id = user_comment.user_post_id
    # Restrict either superuser or post author
    if request.user.is_superuser or request.user.username is user_comment.user_name:
        user_comment.delete()
        return HttpResponseRedirect('/experiencias/' + str(user_post_id))
    else:
        msg = 'Não tem permissões para essa ação!'
        return render(request, 'login.html', {'msg': msg})


def sendmail():
    send_mail('DJANGO MAIL TEST',
              'DJANGO MESSAGE TEST',
              settings.EMAIL_HOST_USER,
              ['josefigueiredo2001@hotmail.com'],
              fail_silently=False)


def aboutUs(request):
    return render(request, 'aboutUs.html')

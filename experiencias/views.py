from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils import timezone
from django.urls import reverse
from .models import UserPost, UserComment, UserVote, UserProfile
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
    post_author = get_object_or_404(User, username=user_post.user_name)
    if request.user.is_authenticated:
        user = request.user
        user_vote_q = UserVote.objects.filter(user=user).filter(post=user_post)
        if len(user_vote_q) > 0:
            user_vote = user_vote_q[0]
        else:
            user_vote = None
        context = {'user_post': user_post, 'user_vote': user_vote, 'post_author': post_author}
    else:
        user_vote = None
        context = {'user_post': user_post, 'user_vote': user_vote, 'post_author': post_author}
    return render(request, 'userpost.html', context)


# Register logic

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
    print(len(check_user))
    ##############################################################################################################
    check_mail = User.objects.filter(email=user_email)
    if len(check_user) == 0 and len(check_mail) == 0:
        user = User.objects.create_user(user_name, user_email, user_pass)
        user.last_name = 'i'
        user.save()
        sendactivationmail(user.email, user.username, user.id)
        email_msg = 'Por favor, verifique o seu email. Deverá ter recebido o link para ativação da sua conta.'
        return render(request, 'login.html', {'email_msg': email_msg})
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
    account_activated = False
    if user is not None:
        account_activated = (user.last_name == 'a')
    if user is not None and account_activated:
        login(request, user)
        return HttpResponseRedirect(reverse('experiencias:index'))
    else:
        if not account_activated:
            msg = "Erro: A sua conta ainda não está ativa"
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
    print(request.POST.get('text'))
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
    if request.user.is_superuser or request.user.username == user_post.user_name:
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
    user_post.usercomment_set.create(user_name=request.user.username, text=comment_text, pub_data=timezone.now(),
                                     parent_comment_id=-1, author_id=request.user.id)
    user_post.save()
    return HttpResponseRedirect('/experiencias/' + str(user_post.id))


def deletecomment(request, user_comment_id):
    time.sleep(1)
    user_comment = UserComment.objects.get(id=user_comment_id)
    user_post_id = user_comment.user_post_id
    # Restrict to either superuser or post author
    if request.user.is_superuser or request.user.username == user_comment.user_name:
        user_comment.delete()
        return HttpResponseRedirect('/experiencias/' + str(user_post_id))
    else:
        msg = 'Não tem permissões para essa ação!'
        return render(request, 'login.html', {'msg': msg})


def sendactivationmail(destination, user_name, user_id):
    link = 'http://localhost:8000/experiencias/activate/' + str(user_id) + '/'
    send_mail('Ative a sua conta',
              'Olá ' + user_name + ', benvindo/a ao Experiências! Por favor clique no seguinte link para ativar a sua conta: ' + link,
              settings.EMAIL_HOST_USER,
              [destination],
              fail_silently=False)


def sendconfirmationmail(destination, user_name):
    send_mail('Conta ativada com sucesso',
              'Olá ' + user_name + ', a sua conta foi ativada com sucesso!',
              settings.EMAIL_HOST_USER,
              [destination],
              fail_silently=False)


def aboutUs(request):
    return render(request, 'aboutUs.html')


def activate(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'activate.html', {'user': user})


def activateuser(request):
    user_pass = request.POST['password']
    user_name = request.POST['user_name']
    user = authenticate(username=user_name, password=user_pass)
    if user is not None:
        user.last_name = 'a'
        user.save()
        login(request, user)
        sendconfirmationmail(user.email, user.username)
        createprofile(request, user.id)
        return HttpResponseRedirect(reverse('experiencias:index'))
    else:
        msg = "Erro: password incorreta"
        context = {'msg': msg, 'user': User.objects.get(username=user_name)}
        return render(request, 'activate.html', context)
    return HttpResponseRedirect(reverse('experiencias:index'))


def reply(request, comment_id):
    comment = UserComment.objects.get(id=comment_id)
    context = {'comment': comment}
    return render(request, 'reply.html', context)


def replycomment(request):
    comment_id = request.POST['comment_id']
    parent_comment_id = request.POST['parent_comment_id']
    user_post_id = request.POST['user_post_id']
    comment_text = request.POST['comment_text']
    reply_to = request.POST['reply_to']

    print(comment_id, parent_comment_id, user_post_id, comment_text)
    print(parent_comment_id == str(-1))

    if parent_comment_id == str(-1):
        final_parent_id = comment_id
    else:
        final_parent_id = parent_comment_id

    # Restrict to authenticated users
    msg = ''
    if not request.user.is_authenticated:
        msg = 'É necessário o Login para fazer comentários!'
        return render(request, 'login.html', {'msg': msg})
    user_post = UserPost.objects.get(id=user_post_id)
    # Comment create in db
    user_post.usercomment_set.create(user_name=request.user.username, text=comment_text, pub_data=timezone.now(),
                                     parent_comment_id=final_parent_id, author_id=request.user.id, reply_to=reply_to)
    user_post.save()
    return HttpResponseRedirect('/experiencias/' + str(user_post.id))


def vote(request, user_post_id):
    # print("entrou no vote")
    user1 = request.user
    post1 = UserPost.objects.get(id=user_post_id)

    if len(UserVote.objects.filter(user=user1).filter(post=post1)) == 0:
        # print(UserVote.objects.filter(user=user1)[0].vote_score)

        #    if UserVote.objects.filter(user=user1)[0].vote_score == 0:
        # print("entrou no primeiro if")
        user_post_update = UserPost.objects.get(id=post1.id)
        if request.POST['action'] == 'upvote':
            # print("entrou no segundo if")
            user_vote = UserVote(user=user1, post=post1, vote_score=1)
            user_post_update.score = user_post_update.score + 1
            user_post_update.save()
        if request.POST['action'] == 'downvote':
            # print("entrou no terceiro if")
            user_vote = UserVote(user=user1, post=post1, vote_score=-1)
            user_post_update.score = user_post_update.score - 1
            user_post_update.save()
        user_vote.save()

    else:
        user_post_update = UserPost.objects.get(id=post1.id)
        # print("entrou no primeiro else")
        user_vote_edit_q = UserVote.objects.filter(user=user1).filter(post=post1)
        user_vote_edit = user_vote_edit_q[0]

        if request.POST['action'] == 'downvote' and user_vote_edit.vote_score == 1:
            # print("dentro do else: downvote e +1")
            user_vote_edit.vote_score = -1
            user_vote_edit.save()
            user_post_update.score = user_post_update.score - 2
            user_post_update.save()

        elif request.POST['action'] == 'downvote' and user_vote_edit.vote_score == -1:
            # print("dentro do else: downvote e -1")
            user_vote_edit.delete()
            #            user_vote_edit.vote_score = 0
            #            user_vote_edit.save()
            user_post_update.score = user_post_update.score + 1
            user_post_update.save()

        elif request.POST['action'] == 'upvote' and user_vote_edit.vote_score == -1:
            # print("dentro do else: upvote e -1")
            user_vote_edit.vote_score = 1
            user_vote_edit.save()
            user_post_update.score = user_post_update.score + 2
            user_post_update.save()

        elif request.POST['action'] == 'upvote' and user_vote_edit.vote_score == 1:
            # print("dentro do else: upvote e +1")
            user_vote_edit.delete()
            #            user_vote_edit.vote_score = 0
            #            user_vote_edit.save()
            user_post_update.score = user_post_update.score - 1
            user_post_update.save()
    return HttpResponseRedirect('/experiencias/' + str(user_post_id))


def createprofile(request, user_id):
    user = User.objects.get(id=user_id)
    profile_text = 'Olá! Bem-vindo(a) à minha página de perfil! :)'
    profile_img = 'https://sumaleeboxinggym.com/wp-content/uploads/2018/06/Generic-Profile-1600x1600.png'
    user_profile = UserProfile(text=profile_text, img=profile_img, username=request.user.username, user=user)
    user_profile.save()


def userprofile(request, user_id):
    # profile_id = user_id.UserProfile.id
    #  user_id.UserProfile
    # profile_id = user_id.UserProfile.id
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    context = {'user_profile': user_profile}

    # return render(request, 'profile.html', context)
    user_post_list = UserPost.objects.filter(user_name=user_profile.username)
    context2 = {'user_post_list': user_post_list}
    context.update(context2)
    return render(request, 'profile.html', context)


def editprofile(request, user_id):
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    # user_profile = UserProfile.objects.get()
    context = {'user_profile': user_profile}
    return render(request, 'editprofile.html', context)


def editLogicProfile(request, user_id):
    profile_text = request.POST['text']
    profile_img = request.POST['img']
    # Restrict to authenticated users
    if not request.user.is_authenticated:
        return HttpResponse('<h1>Não estás logado...</h1>')
    # user_profile = UserProfile.objects.get(user_id)
    user_profile = get_object_or_404(UserProfile, pk=user_id)
    user_profile.text = profile_text
    user_profile.img = profile_img
    user_profile.save()
    return HttpResponseRedirect(reverse('experiencias:index'))

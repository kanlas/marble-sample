from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .common import getPrivacy
from .models import Idea, Follower, PrivacyLevel

# index: list of recent ideas that are public, from follows or from self
def index(request):
    # get all public ideas
    current_user = request.user.username
    latest_idea_list = Idea.objects.filter(privacy='public')
    
    # only do a check for private/protected posts if logged in
    if request.user.is_authenticated:
        # add private self posts
        latest_idea_list = latest_idea_list | Idea.objects.filter(username=current_user)
        # add protected posts from follows
        follows = Follower.objects.filter(username=current_user).exclude(pending=True).values_list('follows')
        latest_idea_list = latest_idea_list | Idea.objects.filter(username__in=follows, privacy='protected')
    
    # sort by create time and show most recent 10
    latest_idea_list = latest_idea_list.order_by('-create_time')[:10]
    context = {'latest_idea_list': latest_idea_list}
    return render(request, 'ideation/index.html', context)


# ideate: form to create a new idea
def ideate(request):
    if request.method == 'POST':
        text = request.POST['idea_text']
        title = request.POST['title']
        privacy = request.POST['privacy']
        idea = Idea()
        idea.title = title
        idea.text = text
        idea.create_time = timezone.now()
        idea.username = request.user.username
        idea.privacy = getPrivacy(privacy)  
        idea.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'ideation/ideate.html')
    
    
# user: shows the username and list of ideas along with option to follow or unfollow
def user(request, username):
    current_user = request.user.username
    existing_follow = Follower.objects.filter(username=current_user, follows=username)

    # process a follow/unfollow request, defined by the existence of a current relationship
    if request.method == 'POST':
        if existing_follow.exists():
            existing_follow.delete()
        else:
            new_follow = Follower()
            new_follow.username = current_user
            new_follow.follows = username
            new_follow.save()
        return HttpResponseRedirect(reverse('index'))

    # get all of the ideas for the requested username
    all_user_ideas = Idea.objects.filter(username=username)
    
    # if looking at another user's profile, exclude private posts
    if username != current_user:
        all_user_ideas = all_user_ideas.exclude(privacy=PrivacyLevel.PRIVATE)
        
    # this has an arbitrary limit of 50 ideas just in case
    all_user_ideas = all_user_ideas.order_by('-create_time')[:50]
    is_following = existing_follow.exists()
    context = {'username': username, 'all_user_ideas': all_user_ideas, 'is_following': is_following }
    return render(request, 'ideation/user.html', context)
    
    
# manage_ideas: used as a base page to then update privacy level or delete an idea
def manage_ideas(request, username):
    current_user = request.user.username
    all_user_ideas = Idea.objects.filter(username=current_user).order_by('-create_time')
    context = { 'all_user_ideas' : all_user_ideas }
    return render(request, 'ideation/manage_ideas.html', context)
 
 
def update_idea(request, username, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    if request.method == 'POST':
        privacy = request.POST['privacy']
        idea.privacy = getPrivacy(privacy)
        idea.save()
        return HttpResponseRedirect(reverse('index'))
    context = {'idea': idea, 'privacy_choices' : PrivacyLevel.choices}
    return render(request, 'ideation/update_idea.html', context)
    

def delete_idea(request, username, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    idea.delete()
    return HttpResponseRedirect(reverse('index')) 
        

def manage_follows(request, username):
    current_user = request.user.username
    all_followers = Follower.objects.filter(follows=current_user).exclude(pending=True)
    all_follows = Follower.objects.filter(username=current_user).exclude(pending=True)
    all_pending = Follower.objects.filter(follows=current_user, pending=True)
    context = { 'all_followers' : all_followers, 'all_follows' : all_follows, 'all_pending' : all_pending}
    return render(request, 'ideation/manage_follows.html', context)
 
 
def remove_follower(request, username, follower):
    follow = Follower.objects.get(username=follower, follows=username)
    follow.delete()
    return HttpResponseRedirect(reverse('follows', args=[username]))
    
def approve_follower(request, username, follower):
    follow = Follower.objects.get(username=follower, follows=username)
    follow.pending = False
    follow.save()
    return HttpResponseRedirect(reverse('follows', args=[username]))
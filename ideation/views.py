from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .common import getApprovedFollows, getApprovedFollowers, getPendingFollowers, getPrivacy, sortIdeas
from .models import Idea, Following, PrivacyLevel

# index: list of recent ideas that are public, from follows or from self
def index(request):
    # get all public ideas
    latest_idea_list = Idea.objects.filter(privacy='public')
    
    # only do a check for private/protected posts if logged in
    if request.user.is_authenticated:
        current_user = request.user.username
        # add private posts from current_user
        latest_idea_list = latest_idea_list | Idea.objects.filter(username=current_user)
        # add protected posts from follows
        follows = getApprovedFollows(current_user).values_list('follows')
        latest_idea_list = latest_idea_list | Idea.objects.filter(username__in=follows, privacy='protected')
    
    # sort by create time and show most recent 10
    context = {'latest_idea_list': sortIdeas(latest_idea_list, 10)}
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
    
    
# user: see recent posts for target_user, follow/unfollow, or manage ideas and follows if self
def user(request, user):
    current_user = request.user.username
    target_user = user
    existing_follow = Following.objects.filter(follower=current_user, follows=target_user)

    # process a follow/unfollow request, defined by the existence of a current relationship
    if request.method == 'POST':
        if existing_follow.exists():
            existing_follow.delete()
        else:
            new_follow = Following()
            new_follow.follower = current_user
            new_follow.follows = target_user
            new_follow.save()
        return HttpResponseRedirect(reverse('index'))

    # get all of the ideas for the requested target_user
    all_user_ideas = Idea.objects.filter(username=target_user)
    
    # if looking at another user's profile, exclude private posts
    if target_user != current_user:
        all_user_ideas = all_user_ideas.exclude(privacy=PrivacyLevel.PRIVATE)
        
    # ideas has an arbitrary limit of 50
    context = { 'target_user' : target_user }
    context['all_user_ideas'] = sortIdeas(all_user_ideas, 50)
    context['is_following'] = existing_follow.exists()
    return render(request, 'ideation/user.html', context)
    
    
# manage_ideas: used as a base page view ideas, update privacy level or delete an idea
def manage_ideas(request, user):
    all_user_ideas = Idea.objects.filter(username=user).order_by('-create_time')
    context = { 'all_user_ideas' : all_user_ideas }
    return render(request, 'ideation/manage_ideas.html', context)
 
 
# change the privacy level on a given idea
def update_idea(request, user, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    if request.method == 'POST':
        privacy = request.POST['privacy']
        idea.privacy = getPrivacy(privacy)
        idea.save()
        return HttpResponseRedirect(reverse('index'))
    context = {'idea': idea, 'privacy_choices' : PrivacyLevel.choices}
    return render(request, 'ideation/update_idea.html', context)
    

# delete the given idea
def delete_idea(request, user, idea_id):
    idea = Idea.objects.get(pk=idea_id)
    idea.delete()
    return HttpResponseRedirect(reverse('index')) 
        

# manage_follows: used as a base page to see all follows and followers and approve/deny
def manage_follows(request, user):
    context = dict()
    context['all_followers'] = getApprovedFollowers(user)
    context['all_follows'] = getApprovedFollows(user)
    context['all_pending'] = getPendingFollowers(user)
    return render(request, 'ideation/manage_follows.html', context)
 
 
# remove a follower or deny a pending request
def remove_follower(request, user, follower):
    follow = Following.objects.get(follower=follower, follows=user)
    follow.delete()
    return HttpResponseRedirect(reverse('follows', args=[user]))

    
# approve a pending follower   
def approve_follower(request, user, follower):
    follow = Following.objects.get(follower=follower, follows=user)
    follow.pending = False
    follow.save()
    return HttpResponseRedirect(reverse('follows', args=[user]))
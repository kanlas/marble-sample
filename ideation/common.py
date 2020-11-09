from .models import Following, PrivacyLevel

def getPrivacy(privacy):   
    selection = PrivacyLevel.PUBLIC
    if privacy == 'protected':
        selection = PrivacyLevel.PROTECTED
    elif privacy == 'private':
        selection = PrivacyLevel.PRIVATE
    return selection
    
def getApprovedFollows(current_user):
    return Following.objects.filter(follower=current_user, pending=False)

def getApprovedFollowers(current_user):
    return Following.objects.filter(follows=current_user, pending=False)
    
def getPendingFollowers(current_user):
    return Following.objects.filter(follows=current_user, pending=True)

def sortIdeas(ideas_list, count):
    return ideas_list.order_by('-create_time')[:count]
    
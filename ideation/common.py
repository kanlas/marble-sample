from .models import PrivacyLevel

def getPrivacy(privacy):   
    selection = PrivacyLevel.PUBLIC
    if privacy == 'protected':
        selection = PrivacyLevel.PROTECTED
    elif privacy == 'private':
        selection = PrivacyLevel.PRIVATE
    return selection
from accounts.models import Profile

def run():
    profiles = Profile.objects.all()

    for profile in profiles:
        print(profile.email, profile.pk)


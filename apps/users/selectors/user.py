from apps.users.models import User

def get_user_by_id(user_id: int):
    return User.objects.get(id=user_id)
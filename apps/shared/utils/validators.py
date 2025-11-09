

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Administrador').exists()
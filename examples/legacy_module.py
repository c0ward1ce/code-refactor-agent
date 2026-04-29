def should_notify(user):
    if user.active:
        return user.email is not None
    return False


def has_access(flag):
    if not flag:
        return False
    return True

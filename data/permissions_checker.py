from flask_login import current_user


def who_are_you():
    role = current_user.role
    if role == 'Admin':
        return 'adm'
    elif role == 'User':
        return 'usr'
    else:
        return 'mdr'

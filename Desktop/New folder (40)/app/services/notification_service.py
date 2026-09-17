from app.domain.notification import Notification
from app.domain.user import User
from app.extensions import db


def create_notification(user_id, title, message, related_request_id=None):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        related_request_id=related_request_id,
    )
    db.session.add(notification)
    return notification


def notify_roles(roles, title, message, related_request_id=None, exclude_user_id=None):
    users = User.query.filter(User.role.in_(roles), User.is_active_user.is_(True)).all()
    notifications = []
    for user in users:
        if exclude_user_id is not None and user.id == exclude_user_id:
            continue
        notifications.append(
            create_notification(
                user.id,
                title,
                message,
                related_request_id=related_request_id,
            )
        )
    return notifications

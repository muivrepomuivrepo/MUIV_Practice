from flask_login import current_user

from app.domain.audit_log import AuditLog
from app.domain.client_request import ClientRequest
from app.domain.request_comment import RequestComment
from app.extensions import db


def create_request(title, description, service_id, object_address, priority):
    request_item = ClientRequest(
        title=title,
        description=description,
        service_id=service_id,
        object_address=object_address,
        priority=priority,
        client_id=current_user.id,
        status="new",
    )
    db.session.add(request_item)
    db.session.flush()
    db.session.add(AuditLog(action="Создана заявка", entity_type="ClientRequest", entity_id=request_item.id, user_id=current_user.id))
    db.session.commit()
    return request_item


def add_comment(request_item, body, is_internal=False):
    comment = RequestComment(
        request_id=request_item.id,
        author_id=current_user.id,
        body=body,
        is_internal=is_internal,
    )
    db.session.add(comment)
    db.session.add(AuditLog(action="Добавлен комментарий", entity_type="ClientRequest", entity_id=request_item.id, user_id=current_user.id))
    db.session.commit()
    return comment

from flask_login import current_user

from app.domain.audit_log import AuditLog
from app.domain.attachment import Attachment
from app.extensions import db
from app.services.notification_service import create_notification, notify_roles
from app.utils.file_uploads import remove_uploaded_file, save_uploaded_file


def add_request_attachment(request_item, file_storage):
    file_data = save_uploaded_file(file_storage, subfolder=f"requests/{request_item.id}")
    if file_data is None:
        return None

    attachment = Attachment(
        request_id=request_item.id,
        uploader_id=current_user.id,
        **file_data,
    )
    db.session.add(attachment)
    db.session.add(
        AuditLog(
            action="Добавлен файл к заявке",
            entity_type="ClientRequest",
            entity_id=request_item.id,
            details=file_data["original_name"],
            user_id=current_user.id,
        )
    )
    if current_user.id == request_item.client_id:
        if request_item.manager_id:
            create_notification(
                request_item.manager_id,
                "Новый файл в заявке",
                f"К заявке #{request_item.id} приложен файл «{file_data['original_name']}».",
                related_request_id=request_item.id,
            )
        else:
            notify_roles(
                ["manager", "admin"],
                "Новый файл в заявке",
                f"К заявке #{request_item.id} приложен файл «{file_data['original_name']}».",
                related_request_id=request_item.id,
                exclude_user_id=current_user.id,
            )
    else:
        create_notification(
            request_item.client_id,
            "Новый файл в заявке",
            f"К заявке #{request_item.id} приложен файл «{file_data['original_name']}».",
            related_request_id=request_item.id,
        )
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        remove_uploaded_file(file_data["stored_name"])
        raise
    return attachment

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User:
    def __init__(
        self,
        email: str,
        password_hash: str,
        full_name: Optional[str] = None,
        user_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id or uuid4()
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update(self, full_name: Optional[str] = None):
        if full_name is not None:
            self.full_name = full_name
        self.updated_at = datetime.utcnow()




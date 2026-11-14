from unicodedata import category, normalize

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.services.access import Role, require_active, require_roles
from app.services.auth import hash_password, normalize_email, verify_password
from app.services.errors import AuthenticationError, ConflictError, InvalidInputError, NotFoundError
from app.services.tasks import now


def normalize_name(value: str, field: str) -> str:
    name = normalize("NFC", value.strip())
    if not 1 <= len(name) <= 100 or any(category(char) in {"Cc", "Zl", "Zp"} for char in name):
        label = "first name" if field == "first_name" else "last name"
        raise InvalidInputError(f"Enter a {label} of 1 to 100 characters on one line.", field=field)
    return name


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _save(self, user: User) -> User:
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError("An account with this email address already exists.") from None
        await self.db.refresh(user)
        return user

    async def register(self, email: str, password: str, *, first_name: str, last_name: str) -> User:
        email = normalize_email(email)
        first_name = normalize_name(first_name, "first_name")
        last_name = normalize_name(last_name, "last_name")
        user = User(email=email, first_name=first_name, last_name=last_name, password_hash=await hash_password(password))
        self.db.add(user)
        return await self._save(user)

    async def login(self, email: str, password: str) -> User:
        # Logowanie nie zmienia się po zmianie konfiguracji domeny rejestracji.
        user = await self.db.scalar(select(User).where(User.email == email.strip().lower()))
        if not await verify_password(password, user.password_hash if user else None):
            raise AuthenticationError("Incorrect email or password.")
        require_active(user)
        return user

    async def list_users(self, actor: User, *, pending: bool | None, limit: int, offset: int):
        require_roles(actor, Role.ADMIN)
        query = select(User).order_by(User.created_at.desc(), User.id.desc())
        if pending is not None:
            query = query.where(User.is_approved == (not pending))
        return list((await self.db.scalars(query.limit(limit).offset(offset))).all())

    async def assignees(self, actor: User, *, limit: int, offset: int):
        require_roles(actor, Role.ADMIN)
        query = select(User).where(User.role == Role.STAFF, User.is_active, User.is_approved)
        return list((await self.db.scalars(query.order_by(User.email, User.id).limit(limit).offset(offset))).all())

    async def set_name(self, actor: User, user_id: int, *, first_name: str, last_name: str) -> User:
        require_active(actor)
        if actor.id != user_id:
            require_roles(actor, Role.ADMIN)
        first_name = normalize_name(first_name, "first_name")
        last_name = normalize_name(last_name, "last_name")
        user = await self._lock(user_id)
        user.first_name, user.last_name = first_name, last_name
        return await self._save(user)

    async def _lock(self, user_id: int) -> User:
        user = await self.db.scalar(select(User).where(User.id == user_id).with_for_update()
                                    .execution_options(populate_existing=True))
        if user is None:
            raise NotFoundError("Nie znaleziono konta.")
        return user

    async def approve(self, actor: User, user_id: int, role: Role) -> User:
        require_roles(actor, Role.ADMIN)
        role = self._role(role)
        user = await self._lock(user_id)
        if user.is_approved:
            raise ConflictError("This account is already approved. Use the change role action.")
        user.role, user.is_approved = role, True
        user.approved_by_id, user.approved_at = actor.id, now()
        return await self._save(user)

    @staticmethod
    def _role(role):
        try:
            return Role(role)
        except (ValueError, TypeError):
            raise InvalidInputError("Select a valid role.", field="role") from None

    async def change_role(self, actor: User, user_id: int, role: Role) -> User:
        require_roles(actor, Role.ADMIN)
        role = self._role(role)
        user = await self._lock(user_id)
        if not user.is_approved:
            raise ConflictError("Approve the account and choose a role first.")
        user.role = role
        return await self._save(user)

    async def set_active(self, actor: User, user_id: int, active: bool) -> User:
        require_roles(actor, Role.ADMIN)
        user = await self._lock(user_id)
        user.is_active = active
        return await self._save(user)

    async def delete_pending(self, actor: User, user_id: int) -> None:
        require_roles(actor, Role.ADMIN)
        user = await self._lock(user_id)
        if user.is_approved:
            raise ConflictError("This account has already been approved. Use Deactivate to block access.")
        await self.db.delete(user)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError("This account is linked to existing records and cannot be deleted.") from None

    async def bootstrap_admin(self, email: str, password: str, *, first_name: str, last_name: str) -> User:
        email = normalize_email(email)
        first_name = normalize_name(first_name, "first_name")
        last_name = normalize_name(last_name, "last_name")
        encoded = await hash_password(password)
        # Serializacja obejmuje wszystkie procesy wykonujące jednorazową komendę.
        await self.db.execute(text("SELECT pg_advisory_xact_lock(730031001)"))
        if await self.db.scalar(select(User.id).where(User.is_approved, User.role == Role.ADMIN).limit(1)):
            raise ConflictError("An administrator already exists. Register and approve the account.")
        if await self.db.scalar(select(User.id).where(User.email == email)):
            raise ConflictError("An account with this email address already exists.")
        user = User(email=email, first_name=first_name, last_name=last_name, password_hash=encoded, role=Role.ADMIN,
                    is_approved=True, is_active=True, approved_at=now())
        self.db.add(user)
        return await self._save(user)

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.services.access import Role, require_active, require_roles
from app.services.auth import hash_password, normalize_email, verify_password
from app.services.errors import AuthenticationError, ConflictError, InvalidInputError, NotFoundError
from app.services.tasks import now


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _save(self, user: User) -> User:
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ConflictError("Konto z tym adresem e-mail już istnieje.") from None
        await self.db.refresh(user)
        return user

    async def register(self, email: str, password: str) -> User:
        email = normalize_email(email)
        user = User(email=email, password_hash=await hash_password(password))
        self.db.add(user)
        return await self._save(user)

    async def login(self, email: str, password: str) -> User:
        # Logowanie nie zmienia się po zmianie konfiguracji domeny rejestracji.
        user = await self.db.scalar(select(User).where(User.email == email.strip().lower()))
        if not await verify_password(password, user.password_hash if user else None):
            raise AuthenticationError("Niepoprawny e-mail lub hasło.")
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
            raise ConflictError("Konto zostało już zaakceptowane. Użyj osobnej zmiany roli.")
        user.role, user.is_approved = role, True
        user.approved_by_id, user.approved_at = actor.id, now()
        return await self._save(user)

    @staticmethod
    def _role(role):
        try:
            return Role(role)
        except (ValueError, TypeError):
            raise InvalidInputError("Wybierz jedną z trzech ról.", field="role") from None

    async def change_role(self, actor: User, user_id: int, role: Role) -> User:
        require_roles(actor, Role.ADMIN)
        role = self._role(role)
        user = await self._lock(user_id)
        if not user.is_approved:
            raise ConflictError("Najpierw zaakceptuj konto, wybierając rolę.")
        user.role = role
        return await self._save(user)

    async def set_active(self, actor: User, user_id: int, active: bool) -> User:
        require_roles(actor, Role.ADMIN)
        user = await self._lock(user_id)
        user.is_active = active
        return await self._save(user)

    async def bootstrap_admin(self, email: str, password: str) -> User:
        email = normalize_email(email)
        encoded = await hash_password(password)
        # Serializacja obejmuje wszystkie procesy wykonujące jednorazową komendę.
        await self.db.execute(text("SELECT pg_advisory_xact_lock(730031001)"))
        if await self.db.scalar(select(User.id).where(User.is_approved, User.role == Role.ADMIN).limit(1)):
            raise ConflictError("Pierwszy administrator już istnieje. Użyj rejestracji i akceptacji konta.")
        if await self.db.scalar(select(User.id).where(User.email == email)):
            raise ConflictError("Konto z tym adresem e-mail już istnieje.")
        user = User(email=email, password_hash=encoded, role=Role.ADMIN,
                    is_approved=True, is_active=True, approved_at=now())
        self.db.add(user)
        return await self._save(user)

from sqlalchemy import String, Integer, Boolean, DateTime,ForeignKey,JSON,delete,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,sessionmaker,relationship
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core import settings
import asyncio

class Base(DeclarativeBase):
    pass

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String(50),nullable=False,unique=True)
    description: Mapped[str] = mapped_column(String(255),nullable=True)
    permissions: Mapped[list[str]] = mapped_column(
        JSON,
        default=["login","post","comment"]

    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id},name={self.name},permissions={self.permissions},users={self.users})>"

class User(Base):
    __tablename__ = 'users'
    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    username : Mapped[str] = mapped_column(String(50),nullable=False,unique=True)
    email : Mapped[str] = mapped_column(String(100),nullable=True,unique=True)
    hashed_password : Mapped[str] = mapped_column(String(255),nullable=False)
    is_active : Mapped[bool] = mapped_column(Boolean,default=True)
    created_at : Mapped[datetime] = mapped_column(DateTime,default=datetime.utcnow)
    role_id : Mapped[int] = mapped_column(ForeignKey("roles.id"),nullable=False,default=3)
    role: Mapped[Role] = relationship("Role", back_populates="users")
    def __repr__(self) -> str:
        return f"<User(id={self.id},username={self.username},role={self.role.name})>"

async def main():
    DATABASE_URL = settings.database_url
    engine = create_async_engine(DATABASE_URL,echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(delete(User))
            await db.execute(delete(Role))

            await db.commit()
            roles = [
                Role(id=1, name="admin", description="管理员", permissions=["all"]),
                Role(id=2, name="moderator", description="版主", permissions=["login", "post", "comment", "delete_post"]),
                Role(id=3, name="user", description="普通用户", permissions=["login", "post", "comment"]),
                Role(id=4, name="muted", description="被禁言", permissions=["login", "comment"]),
                Role(id=5, name="banned", description="被封禁", permissions=[])
            ]
            db.add_all(roles)
            await db.commit()

            admin_user = User(
                id=1,
                username="admin",
                email="admin@example.com",
                hashed_password="hashed_admin123",
                role_id=1
            )

            normal_user = User(
                id=2,
                username="normal_user",
                email="normal_user@example.com",
                hashed_password="hashed_normal123",
                role_id=3
            )
            db.add_all([admin_user, normal_user])
            await db.commit()

            stmt = select(User).where(User.username == "admin")
            result = await db.execute(stmt)
            user=result.scalar_one()
            print(f"用户信息：{user}")
            print(f"用户 {user.username} 的角色：{user.role.name}")
            print(f"用户 {user.username} 的权限：{user.role.permissions}")
        except Exception as e:
            await db.rollback()
            print("错误",e)
        finally:
            await db.close()
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(main())

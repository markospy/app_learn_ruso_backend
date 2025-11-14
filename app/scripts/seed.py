"""Script to seed initial data: roles and admin user."""
from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.database import engine, init_db
from app.models.role import Role
from app.models.user import User


def seed_roles(session: Session) -> None:
    """Create initial roles if they don't exist."""
    roles_data = [
        {"id": 1, "name": "admin"},
        {"id": 2, "name": "teacher"},
        {"id": 3, "name": "student"},
    ]

    for role_data in roles_data:
        existing_role = session.get(Role, role_data["id"])
        if not existing_role:
            role = Role(**role_data)
            session.add(role)
            print(f"Created role: {role_data['name']}")
        else:
            print(f"Role already exists: {role_data['name']}")

    session.commit()


def seed_admin_user(session: Session) -> None:
    """Create default admin user if it doesn't exist."""
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "admin123"  # Change this in production!

    # Check if admin user exists
    statement = select(User).where(User.username == admin_username)
    existing_user = session.exec(statement).first()

    if not existing_user:
        admin_user = User(
            name="Administrator",
            email=admin_email,
            username=admin_username,
            password=get_password_hash(admin_password),
            language="es",
            id_rol=1,  # admin role
            is_active=True,
        )
        session.add(admin_user)
        session.commit()
        print(f"Created admin user: {admin_username}")
        print(f"Password: {admin_password} (CHANGE THIS IN PRODUCTION!)")
    else:
        print(f"Admin user already exists: {admin_username}")


def main() -> None:
    """Main seeding function."""
    print("Initializing database...")
    init_db()

    print("Seeding roles...")
    with Session(engine) as session:
        seed_roles(session)

    print("Seeding admin user...")
    with Session(engine) as session:
        seed_admin_user(session)

    print("Seeding completed!")


if __name__ == "__main__":
    main()


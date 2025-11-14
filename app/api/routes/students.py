from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import get_current_active_user
from app.database import get_session
from app.models.user import LinkStudentTeacher, User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("", response_model=List[UserPublic])
def list_students(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> List[UserPublic]:
    """List students linked to the current teacher."""
    if not current_user.role or current_user.role.name != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher role"
        )

    statement = select(LinkStudentTeacher).where(
        LinkStudentTeacher.id_teacher == current_user.id
    )
    links = session.exec(statement).all()

    students = []
    for link in links:
        student = session.get(User, link.id_student)
        if student:
            students.append(student)

    return [UserPublic.model_validate(student) for student in students]


@router.post("/{student_id}/link", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def link_student(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> UserPublic:
    """Link a student to the current teacher."""
    if not current_user.role or current_user.role.name != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher role"
        )

    student = session.get(User, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    if student.id_rol != 3:  # student role
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a student"
        )

    # Check if link already exists
    statement = select(LinkStudentTeacher).where(
        LinkStudentTeacher.id_student == student_id,
        LinkStudentTeacher.id_teacher == current_user.id
    )
    existing_link = session.exec(statement).first()

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already linked to this teacher"
        )

    # Create link
    link = LinkStudentTeacher(
        id_student=student_id,
        id_teacher=current_user.id
    )
    session.add(link)
    session.commit()

    return UserPublic.model_validate(student)


@router.delete("/{student_id}/unlink", status_code=status.HTTP_204_NO_CONTENT)
def unlink_student(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> None:
    """Unlink a student from the current teacher."""
    if not current_user.role or current_user.role.name != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher role"
        )

    statement = select(LinkStudentTeacher).where(
        LinkStudentTeacher.id_student == student_id,
        LinkStudentTeacher.id_teacher == current_user.id
    )
    link = session.exec(statement).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )

    session.delete(link)
    session.commit()


@router.get("/{student_id}/progress")
def get_student_progress(
    student_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> dict:
    """Get student progress (teacher only)."""
    if not current_user.role or current_user.role.name != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires teacher role"
        )

    # Verify link exists
    statement = select(LinkStudentTeacher).where(
        LinkStudentTeacher.id_student == student_id,
        LinkStudentTeacher.id_teacher == current_user.id
    )
    link = session.exec(statement).first()

    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not linked to this teacher"
        )

    # TODO: Implement actual progress tracking
    return {
        "student_id": student_id,
        "progress": {
            "verbs_learned": 0,
            "nouns_learned": 0,
            "total_practice_sessions": 0,
        }
    }


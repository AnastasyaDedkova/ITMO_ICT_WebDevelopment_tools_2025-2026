from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/", response_model=list[ProfileRead])
def get_profiles(session: Session = Depends(get_session)):
    profiles = session.exec(select(Profile)).all()
    return profiles


@router.get("/{profile_id}", response_model=ProfileRead)
def get_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/", response_model=ProfileRead)
def create_profile(profile_data: ProfileCreate, session: Session = Depends(get_session)):
    profile = Profile(**profile_data.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.patch("/{profile_id}", response_model=ProfileRead)
def update_profile(profile_id: int, profile_data: ProfileUpdate, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, session: Session = Depends(get_session)):
    profile = session.get(Profile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    session.delete(profile)
    session.commit()
    return {"message": "Profile deleted"}
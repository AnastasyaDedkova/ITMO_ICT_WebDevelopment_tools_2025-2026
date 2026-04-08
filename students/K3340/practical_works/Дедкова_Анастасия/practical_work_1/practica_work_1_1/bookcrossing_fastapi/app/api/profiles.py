from fastapi import APIRouter, HTTPException
from app.schemas.profile import Profile

router = APIRouter(prefix="/profiles", tags=["Profiles"])

temp_profiles = [
    {
        "id": 1,
        "username": "andrey",
        "city": "Moscow"
    },
    {
        "id": 2,
        "username": "maria",
        "city": "Saint Petersburg"
    }
]


@router.get("/", response_model=list[Profile])
def get_profiles():
    return temp_profiles


@router.get("/{profile_id}", response_model=Profile)
def get_profile(profile_id: int):
    for profile in temp_profiles:
        if profile["id"] == profile_id:
            return profile
    raise HTTPException(status_code=404, detail="Profile not found")


@router.post("/", response_model=Profile)
def create_profile(profile: Profile):
    new_profile = profile.model_dump()
    new_profile["id"] = len(temp_profiles) + 1
    temp_profiles.append(new_profile)
    return new_profile


@router.delete("/{profile_id}")
def delete_profile(profile_id: int):
    for i, profile in enumerate(temp_profiles):
        if profile["id"] == profile_id:
            deleted = temp_profiles.pop(i)
            return {"message": "Profile deleted", "profile": deleted}
    raise HTTPException(status_code=404, detail="Profile not found")
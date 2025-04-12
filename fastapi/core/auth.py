from fastapi import Depends
from main import app
MOCK_USER={"name": "Erik",
           "id":"73091836-59ed-44d6-9e04-b3bdcdf1928d",
           "role": "admin",
           "daypass_tokens":5}


# Mock function to simulate getting the current user
async def get_current_user():
    if app.state.is_user_logged_in == True:
        # Return the mocked user if "logged in" (based on the flag)
        return MOCK_USER
    else:
        return None

# Dependency injection to get the current user
async def current_user(user=Depends(get_current_user)):
    return user
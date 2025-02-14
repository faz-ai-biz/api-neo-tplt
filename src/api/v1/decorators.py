from functools import wraps

from fastapi import HTTPException, status


def handle_file_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except PermissionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to access file",
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return wrapper

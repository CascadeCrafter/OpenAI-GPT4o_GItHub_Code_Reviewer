import uvicorn
from dotenv import load_dotenv

from app.api import app

# Load environment variables from .env file
load_dotenv()


def main():
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()

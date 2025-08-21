# main.py
import sys
from gui import App

from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

api_key = load_dotenv(dotenv_path=BASE_DIR / ".env")

def main():
    # print(BASE_DIR)
    # print(api_key)
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()

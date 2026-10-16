import os
from dotenv import load_dotenv

load_dotenv()  # or load_dotenv(r"F:\final_proj_DS\.env")
k = os.getenv("GROK_API_KEY")
print(repr(k[:4]) if k else None, len(k) if k else 0)
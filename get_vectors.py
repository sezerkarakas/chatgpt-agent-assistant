from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI() # API keyinizi buraya girin


vector_stores = client.vector_stores.list()
with open("vector_stores.json", "w") as f:
    json.dump(vector_stores.model_dump(), f, indent=4)
print(vector_stores)
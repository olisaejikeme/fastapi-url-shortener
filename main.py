import hashlib

import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import RedirectResponse

app = FastAPI()


class URL(BaseModel):
    original_url: str

def shorten_url(original_url: str) -> str:
    hash_obj = hashlib.md5(original_url.encode())
    shortened_url = hash_obj.hexdigest()[:10] # First 10 characters
    return shortened_url

def save_url_to_db(original_url: str, shortened_url: str):
    connection = psycopg2.connect("dbname=urls user=user password=password host=localhost")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO urls (original_url, shortened_url) VALUES (%s, %s)",
                   (original_url, shortened_url))
    connection.commit()
    cursor.close()
    connection.close()

@app.post("/shorten")
def shorten_url(url: URL):
    shortened_url = hashlib.md5(url.original_url.encode()).hexdigest()[:10]
    save_url_to_db(url.original_url, shortened_url)
    return {"shortened_url": shortened_url}


@app.get("/{shortened_url}")
def redirect_to_original(shortened_url: str):
    connection = psycopg2.connect("dbname=urls user=user password=password host=localhost")
    cursor = connection.cursor()

    ori = cursor.execute("SELECT original_url FROM urls WHERE shortened_url = %s", (shortened_url,))

    connection.commit()
    result = cursor.fetchone()

    cursor.close()
    connection.close()
    if result:
        return result
    else:
        return {"error": "URL not found"}


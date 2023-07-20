from fastapi import FastAPI, Request
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.config import Config
from starlette.datastructures import URL
from starlette.types import ASGIApp
import ssl
import uvicorn
from libs import cert_gen 

app = FastAPI()

# Your FastAPI routes go here
@app.get("/")
async def read_root():
    return {"Hello": "World"}

def get_ssl_context():
    with open("self_signed_private_key.pem", "rb") as key_file:
        private_key = key_file.read()
    with open("self_signed_certificate.pem", "rb") as cert_file:
        certificate = cert_file.read()

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="self_signed_certificate.pem", keyfile="self_signed_private_key.pem")
    return ssl_context

def run_ssl_server(app: ASGIApp):
    config = Config(".env")
    uvicorn.run(
        app,
        host=config("HOST", default="localhost"),
        port=config("PORT", cast=int, default=8001),
        ssl_version=ssl.PROTOCOL_TLS,
        ssl_keyfile="self_signed_private_key.pem",
        ssl_certfile="self_signed_certificate.pem",
        workers=config("WORKERS", cast=int, default=1),
    )

@app.middleware("http")
async def redirect_to_https(request: Request, call_next):
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
    if forwarded_proto == "http":
        url = URL(request.url)
        url = url.replace(scheme="https")
        response = RedirectResponse(url=url)
        return response
    return await call_next(request)

if __name__ == "__main__":
    pr_key, singed_cert = cert_gen.generate_self_signed_certificate()
    cert_gen.save_self_signed_certificate(private_key_pem=pr_key,certificate_pem=singed_cert)
    ssl_context = get_ssl_context()

    # Run the server with SSL/TLS enabled
    run_ssl_server(app)

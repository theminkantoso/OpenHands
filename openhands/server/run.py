import uvicorn

if __name__ == "__main__":
    uvicorn.run("openhands.server.listen:app", host="127.0.0.1", port=3000, reload=True)
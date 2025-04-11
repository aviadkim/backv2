import uvicorn

if __name__ == "__main__":
    print("Starting Document Understanding API on http://localhost:8000")
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=8000, reload=True)

from pyngrok import ngrok

# Open a tunnel to FastAPI running on port 8000
public_url = ngrok.connect(8000)
print("Public URL:", public_url)
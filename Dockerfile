from python:3.13
workdir /usr/local/app

env PYTHONUNBUFFERED=1

copy requirements.txt ./
run pip install --no-cache-dir -r requirements.txt

copy . .

expose 8000

env IP=0.0.0.0 PORT=8000

cmd ["python", "main.py"]

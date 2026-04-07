FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY application/ .
# Expose BOTH ports
EXPOSE 6000 3000

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port 6000 & streamlit run streamlit_app.py --server.port 3000 --server.address 0.0.0.0"
FROM python:3.9-slim

# Tor kurulumu
RUN apt-get update && apt-get install -y tor

# Tor konfigürasyonu
RUN echo "SocksPort 9050" > /etc/tor/torrc && \
    echo "ControlPort 9051" >> /etc/tor/torrc && \
    echo "CookieAuthentication 0" >> /etc/tor/torrc

# Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Uygulama
COPY app.py /app/app.py

EXPOSE 8000

# Tor'u başlat ve uygulamayı çalıştır
CMD ["sh", "-c", "tor & sleep 5 && python /app/app.py"]

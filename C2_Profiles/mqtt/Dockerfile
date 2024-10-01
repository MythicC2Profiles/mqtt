FROM itsafeaturemythic/mythic_python_base:latest
RUN pip install --upgrade pip
RUN pip install "paho-mqtt<2.0.0" requests

WORKDIR /Mythic/
COPY [".", "."]
CMD ["python3", "main.py"]


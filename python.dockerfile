FROM python:3.6
# RUN mkdir -p /usr/src/app
# WORKDIR /usr/src/app

# COPY requirement.txt /usr/src/app/
# RUN pip3 install --no-cache-dir -r requirement.txt

# COPY . /usr/src/app
# WORKDIR /usr/src/app/
# ENTRYPOINT ["python3"]
# CMD ["api.py"]
# WORKDIR /usr/src/app/
# RUN ls
# ENTRYPOINT ["api.py"]
# CMD [ "python3" ]

WORKDIR /usr/src/app

COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

COPY . .
CMD [ "python", "api.py" ]
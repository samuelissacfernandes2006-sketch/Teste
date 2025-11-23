
# 
FROM python:3.9
# 
WORKDIR /codigo
# 
COPY ./requirements.txt /codigo/requirements.txt
# 
RUN pip install --no-cache-dir --upgrade -r /codigo/requirements.txt
# 
COPY ./codigo /codigo/APP
#
EXPOSE "3019"
# 
CMD ["uvicorn", "APP:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "3019"]

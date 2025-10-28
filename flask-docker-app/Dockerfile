FROM public.ecr.aws/amazonlinux/amazonlinux:2022
RUN yum install -y python3 python3-pip && \
    pip3 install --upgrade pip

RUN alias python=python3

ENV PLATFORM 'Amazon ECS'
ENV PORT 8000

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

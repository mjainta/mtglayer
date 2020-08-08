FROM amazonlinux:2

WORKDIR /usr/src/app

RUN yum -y install zip python3 python3-pip
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/mtgcrawler

CMD [ "python", "./launcher.py" ]

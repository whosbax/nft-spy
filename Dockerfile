FROM debian:latest
WORKDIR /root/app
COPY . .

RUN apt -y update && apt-get install -y cron make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev procps \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl python3 git python3-pip python3-venv

RUN pip install -r ./requirements.txt
RUN python3 ./api.py &
COPY _docker/cron.d/nftspy /etc/cron.d/
RUN crontab /etc/cron.d/nftspy && service cron start

#RUN for py_file in $( find -type f -name "*.py" );do pycodestyle --show-source --show-pep8 $py_file; done;
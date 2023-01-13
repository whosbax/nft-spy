FROM debian:latest
WORKDIR /root/app
COPY . .

RUN apt -y update && apt-get install -y netcat cron make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev procps \
libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl python3 git python3-pip python3-venv

RUN pip install -r ./requirements.txt

RUN touch /var/log/nftspy.log && touch /var/log/flask.log
COPY _docker/init.d/nftspy /etc/init.d/nftspy
RUN chmod +x _docker/init.d/nftspy && chmod 755 /etc/init.d/nftspy && update-rc.d nftspy defaults
RUN for py_file in $( find -type f -name "*.py" );do pycodestyle --show-source --show-pep8 $py_file; done;

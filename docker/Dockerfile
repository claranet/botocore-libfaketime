FROM centos:centos7.4.1708

RUN yum install -y epel-release
RUN yum install -y libfaketime
RUN yum install -y python2-pip

RUN pip install --upgrade pip
RUN pip install boto3==1.4.7
RUN pip install awscli

ENV LD_PRELOAD /usr/lib64/faketime/libfaketime.so.1
ENV FAKETIME_TIMESTAMP_FILE /etc/faketimerc
ENV FAKETIME_NO_CACHE 1

RUN echo "+3d" > /etc/faketimerc

COPY *.whl /

RUN pip install /*.whl

COPY test.py /

CMD python /test.py

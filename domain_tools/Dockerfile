FROM python:3.6.5 As builder
COPY requirements.txt .
RUN  pip3 install --upgrade pip && pip3 install  -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
FROM python:3.6.15-slim 
COPY --from=builder /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages
#Set System TimeZone
#Set 阿里云软件更新源
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN mkdir -p /app/op-kube-manage-api && chmod 775 -R /app/

WORKDIR /app/op-kube-manage-api
COPY . .
CMD  python op_domain_check_v2.py

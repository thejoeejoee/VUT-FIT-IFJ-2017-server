#!/usr/bin/env bash

files="content locale product ifj templates web manage.py requirements.txt conf";
>&2 echo "Packing and transferring...";
tar czf - ${files} | ssh josefkolar.cz "cd /home/ifj/ifj.cz/ && cat - > deploy.tar.gz";
ssh josefkolar.cz << SSH
cd /home/ifj/ifj.cz/;
cp ifj/settings.py .;
tar xvzf deploy.tar.gz;
cp settings.py ifj/settings.py;
cp /home/ifj/ifj.cz/conf/ifj.nginx /etc/nginx/sites-available/;
cp /home/ifj/ifj.cz/conf/ifj.gunicorn.service /etc/systemd/system/;
chown www-data:www-data -R /home/ifj/ifj.cz/;
source /home/ifj/ifj.cz/.venv/bin/activate;
pip install -r /home/ifj/ifj.cz/requirements.txt;
rm -rf /home/ifj/ifj.cz/static/*;
/home/ifj/ifj.cz/manage.py collectstatic --noinput;
service nginx restart;
systemctl daemon-reload;
systemctl restart ifj.gunicorn.service;
SSH

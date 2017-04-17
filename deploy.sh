#!/usr/bin/env bash


ssh bigrs.alien9.net -t "sudo chown -R tiago.tiago works/bigrs_django"
rsync -rCv  --exclude-from 'exclude-list.txt' bigrs bigrs.alien9.net:works/bigrs_django/
rsync -rCv vector bigrs.alien9.net:works/bigrs_django/
scp bigrs/bigrs/settings.production.py bigrs.alien9.net:works/bigrs_django/bigrs/bigrs/settings.py
ssh bigrs.alien9.net -t "sudo chown -R www-data:www-data works/bigrs_django;touch reload"

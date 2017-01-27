

#ssh bigrs.alien9.net -t "rm -rf works/bigrs;mkdir works/bigrs"
rsync -rCv ../bigrs/* bigrs.alien9.net:works/bigrs/
scp config.production.py bigrs.alien9.net:works/bigrs/config.py
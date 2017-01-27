

ssh bigrs.alien9.net -t "rm -rf works/bigrs;mkdir works/bigrs"
scp -rC ../bigrs/* bigrs.alien9.net:works/bigrs/
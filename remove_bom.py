#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
for file in glob.glob("./marcas-e-modelos/*.csv"):
    s = open(file, mode='r', encoding='utf-8-sig').read()
    open(file.replace("los/","los/cle)an/"), mode='w', encoding='utf-8').write(s)











    configure arguments: --with-cc-opt='-g -O2 -fPIE -fstack-protector-strong -Wformat -Werror=format-security -Wdate-time -D_FORTIFY_SOURCE=2' --with-ld-opt='-Wl,-Bsymbolic-functions -fPIE -pie -Wl,-z,relro -Wl,-z,now' --prefix=/usr/share/nginx --conf-path=/etc/nginx/nginx.conf --http-log-path=/var/log/nginx/access.log --error-log-path=/var/log/nginx/error.log --lock-path=/var/lock/nginx.lock --pid-path=/run/nginx.pid --http-client-body-temp-path=/var/lib/nginx/body --http-fastcgi-temp-path=/var/lib/nginx/fastcgi --http-proxy-temp-path=/var/lib/nginx/proxy --http-scgi-temp-path=/var/lib/nginx/scgi --http-uwsgi-temp-path=/var/lib/nginx/uwsgi --with-debug --with-pcre-jit --with-ipv6 --with-http_ssl_module --with-http_stub_status_module --with-http_realip_module --with-http_auth_request_module --with-http_v2_module --with-http_dav_module --with-http_slice_module --with-threads --with-http_addition_module --with-http_dav_module --with-http_flv_module --with-http_geoip_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_image_filter_module --with-http_mp4_module --with-http_perl_module --with-http_random_index_module --with-http_secure_link_module --with-http_v2_module --with-http_sub_module --with-http_xslt_module --with-mail --with-mail_ssl_module --with-stream --with-stream_ssl_module --with-threads --add-module=/build/nginx-1.12.2/debian/modules/headers-more-nginx-module --add-module=/build/nginx-1.12.2/debian/modules/nginx-auth-pam --add-module=/build/nginx-1.12.2/debian/modules/nginx-cache-purge --add-module=/build/nginx-1.12.2/debian/modules/nginx-dav-ext-module --add-module=/build/nginx-1.12.2/debian/modules/nginx-development-kit --add-module=/build/nginx-1.12.2/debian/modules/nginx-echo --add-module=/build/nginx-1.12.2/debian/modules/ngx-fancyindex --add-module=/build/nginx-1.12.2/debian/modules/nchan --add-module=/build/nginx-1.12.2/debian/modules/nginx-lua --add-module=/build/nginx-1.12.2/debian/modules/nginx-upload-progress --add-module=/build/nginx-1.12.2/debian/modules/nginx-upstream-fair --add-module=/build/nginx-1.12.2/debian/modules/ngx_http_substitutions_filter_module --add-module=/build/nginx-1.12.2/debian/modules/passenger/src/nginx_module





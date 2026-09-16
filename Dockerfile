# inspired by https://oneuptime.com/blog/post/2026-02-08-how-to-create-a-dockerfile-for-a-static-website
FROM nginx:alpine

# remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf
# copy our own nginx config
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
# copy HTTP auth password file
COPY ./.htpasswd /etc/nginx/.htpasswd

# copy static site files to nginx default directory
COPY ./site /usr/share/nginx/html/kth-digital-research-handbook

# select port number that the container exposes
EXPOSE 80

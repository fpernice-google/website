FROM nginx:latest

# Configure nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf
ADD external /usr/external/nginx/html/

CMD ["nginx"]
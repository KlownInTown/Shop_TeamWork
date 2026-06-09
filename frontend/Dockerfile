FROM nginx:1.25-alpine

# Удаляем стандартный конфиг Nginx и копируем наш
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
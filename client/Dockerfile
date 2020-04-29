FROM node:14.0.0-alpine as websrc
WORKDIR /app
COPY package*.json /app/
RUN npm install
COPY ./ /app/
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=websrc /app/public/ /usr/share/nginx/html
EXPOSE 80
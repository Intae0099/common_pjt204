# 1. Build Stage
FROM node:18-slim As builder
WORKDIR /app

# Best Practice 적용 (캐싱 최적화)
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# 2. Run Stage
FROM nginx:stable-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
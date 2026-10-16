# ---- build stage: Node compiles the React app to static files ----
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# ---- runtime stage: unprivileged Nginx serves dist/ (no Node, runs as uid 101) ----
FROM nginxinc/nginx-unprivileged:1.29-alpine
LABEL org.opencontainers.image.source="https://github.com/MadaraUchiha-tech/devsecops-python" \
      org.opencontainers.image.description="CareSlot clinic front-desk UI (React + Nginx)"
USER root
RUN apk upgrade --no-cache && rm -f /etc/nginx/conf.d/default.conf
USER 101
ENV BACKEND_URL=http://backend:8000
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1

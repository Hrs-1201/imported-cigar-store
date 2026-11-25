FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG API_ORIGIN=http://127.0.0.1:8000
ARG NEXT_PUBLIC_API_BASE_URL=/api/v1
ENV API_ORIGIN=$API_ORIGIN
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]

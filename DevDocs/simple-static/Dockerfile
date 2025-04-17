FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY server.js .
COPY index-proper.html .

ENV PORT=3002

EXPOSE 3002

CMD ["node", "server.js"]

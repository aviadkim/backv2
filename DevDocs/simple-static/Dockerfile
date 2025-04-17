FROM node:18-alpine

WORKDIR /app

COPY server.js .
COPY index.html .

ENV PORT=3002

EXPOSE 3002

CMD ["node", "server.js"]

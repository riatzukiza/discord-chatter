FROM node:16

USER node

RUN mkdir /home/node/app/ && chown -R node:node /home/node/app
WORKDIR /home/node/app
COPY --chown=node:node package.json package-lock.json ./
RUN npm set audit false
RUN npm install

COPY --chown=node:node . .

CMD ["node", "./index.js"]

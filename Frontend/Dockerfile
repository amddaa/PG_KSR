FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
# COPY yarn.lock ./

RUN npm install
# RUN yarn install

COPY . .

RUN npm run build
# RUN yarn build

CMD ["npm", "start"]
# CMD ["yarn", "start"]

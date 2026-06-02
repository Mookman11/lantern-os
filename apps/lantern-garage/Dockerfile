# Stage 1: Build dependencies
FROM node:22-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --production

# Stage 2: Runtime
FROM node:22-alpine

RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001

WORKDIR /app

COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .

USER nodejs

ENV NODE_ENV=production
ENV PORT=8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8080', (r) => r.statusCode === 200 ? process.exit(0) : process.exit(1))"

CMD ["npm", "run", "start:cloud"]

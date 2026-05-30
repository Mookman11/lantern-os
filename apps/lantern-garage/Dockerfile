FROM node:22-alpine

WORKDIR /repo

COPY apps/lantern-garage/package*.json ./apps/lantern-garage/
RUN cd apps/lantern-garage && npm install --omit=dev

COPY apps/lantern-garage ./apps/lantern-garage
COPY artifacts ./artifacts
COPY data ./data
COPY docs ./docs
COPY manifests ./manifests
COPY reports ./reports
COPY skills ./skills

ENV NODE_ENV=production
ENV PORT=8080

EXPOSE 8080

WORKDIR /repo/apps/lantern-garage
CMD ["npm", "run", "start:cloud"]

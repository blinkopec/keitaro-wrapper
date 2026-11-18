# syntax=docker/dockerfile:1

FROM oven/bun:1

WORKDIR /app

COPY frontend/package.json ./
RUN bun install

COPY frontend ./

EXPOSE 5173

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

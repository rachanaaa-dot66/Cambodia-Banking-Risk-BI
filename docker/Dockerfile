FROM postgres:16-alpine

ENV POSTGRES_DB=banking_risk_bi
ENV POSTGRES_USER=banking_user
ENV POSTGRES_PASSWORD=banking2024

# Copy init scripts — run automatically on first container start
COPY init/ /docker-entrypoint-initdb.d/

EXPOSE 5432

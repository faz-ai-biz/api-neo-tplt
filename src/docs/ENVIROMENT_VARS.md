# Environment Variables Documentation
**official docs**
**version** 0.0.1

## 🔧 Project Settings

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| PROJECT_NAME | "Set-Project-Name" | "Set-Project-Name" | "Set-Project-Name" | Name of the project/service |
| API_VERSION | "1.0.0" | "1.0.0" | "1.0.0" | API version identifier |
| ENVIRONMENT | "dev" | "test" | "prod" | Current environment |
| COMPOSE_PROJECT_NAME | "set-project-name" | "set-project-name" | "set-project-name" | Docker compose project name |

## 🌐 Server Settings

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| HOST | "127.0.0.1" | "0.0.0.0" | "0.0.0.0" | Server host address |
| PORT | 8000 | 8000 | 8000 | Server port number |

## ⚡ Rate Limiting

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| LOGIN_RATE_LIMIT_REQUESTS | 20 | 50 | 20 | Login endpoint rate limit |
| LOGIN_RATE_LIMIT_WINDOW | 60 | 60 | 60 | Rate limit window in seconds |

## 🔒 Authentication

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| AUTH_ALGORITHM | "HS256" | "HS256" | "HS256" | JWT signing algorithm |
| AUTH_SECRET_KEY | **Required** | **Required** | **Required** | JWT signing key |
| AUTH_REFRESH_SECRET_KEY | **Required** | **Required** | **Required** | Refresh token signing key |
| AUTH_TOKEN_AUDIENCE | "fastapi-users" | "fastapi-users" | "fastapi-users" | JWT audience claim |
| AUTH_TOKEN_ISSUER | "fastapi-auth-service" | "fastapi-auth-service" | "fastapi-auth-service" | JWT issuer claim |
| ACCESS_TOKEN_EXPIRE_MINUTES | 15 | 15 | 15 | Access token lifetime |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | 7 | 7 | Refresh token lifetime |

## 🌍 CORS Settings

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| ALLOWED_ORIGINS | "*" | "http://localhost:3000" | "https://example.com" | Allowed CORS origins |

## 💾 Database Settings

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| POSTGRES_DB | **app-name-dev** | **app-name-test**| **app-name-prod** | Database name |
| POSTGRES_HOST | **db-dev** | **db-test** | **db-prod**| Database host |
| POSTGRES_PASSWORD | **Required** | **Required** | **Required** | Database password |
| POSTGRES_PORT | 5432 | 5432 | 5432 | Database port |
| POSTGRES_USER | **set-db-user** | **set-db-user** | **set-db-user** | Database username |


## 📦 Redis Configuration

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| REDIS_URL | "redis://redis:6379/0" | "redis://redis:6379/0" | "redis://redis:6379/0" | Redis connection URL |

## 📝 Logging Configuration

| Environment | Dev | Test | Prod | Description |
|----------|-------------|------|------------|-------------|
| LOG_LEVEL | "DEBUG" | "DEBUG" | "INFO" | Logging level |

### Notes

* Values marked as **Required** must be explicitly set
* N/A indicates the variable is not applicable in that environment
* String values are shown in quotes
* Legacy variables are not included in this format for clarity

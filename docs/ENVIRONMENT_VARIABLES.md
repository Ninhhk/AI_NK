# Environment Variables Reference Guide

This comprehensive guide documents all environment variables used in the AI NVCB project. These variables control application behavior, security settings, performance optimization, and deployment configurations.

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific values
3. For development, also copy:
   ```bash
   cp .env.development .env.local
   ```

## Core Application Settings

### Basic Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | string | `"AI NVCB"` | Application display name |
| `APP_VERSION` | string | `"1.0.0"` | Application version |
| `APP_DESCRIPTION` | string | `"AI-powered presentation generator"` | Application description |
| `DEBUG` | boolean | `false` | Enable debug mode (development only) |
| `ENVIRONMENT` | enum | `"development"` | Environment: `development`, `staging`, `production` |
| `SECRET_KEY` | string | *required* | Secret key for JWT tokens and encryption |
| `TIMEZONE` | string | `"UTC"` | Application timezone |
| `LANGUAGE` | string | `"en"` | Default language code |

### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | `"0.0.0.0"` | Server bind address |
| `PORT` | integer | `8000` | Server port number |
| `RELOAD` | boolean | `false` | Enable auto-reload (development only) |
| `WORKERS` | integer | `1` | Number of worker processes |
| `MAX_CONNECTIONS` | integer | `1000` | Maximum concurrent connections |
| `KEEP_ALIVE_TIMEOUT` | integer | `5` | Keep-alive timeout in seconds |
| `GRACEFUL_TIMEOUT` | integer | `30` | Graceful shutdown timeout |
| `CLIENT_TIMEOUT` | integer | `30` | Client request timeout |

## AI and Model Configuration

### Ollama Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OLLAMA_HOST` | string | `"http://localhost:11434"` | Ollama server URL |
| `OLLAMA_MODEL` | string | `"llama2"` | Default model for text generation |
| `OLLAMA_TIMEOUT` | integer | `120` | Request timeout in seconds |
| `OLLAMA_MAX_RETRIES` | integer | `3` | Maximum retry attempts |
| `OLLAMA_RETRY_DELAY` | integer | `1` | Delay between retries in seconds |
| `OLLAMA_TEMPERATURE` | float | `0.7` | Model creativity/randomness (0.0-1.0) |
| `OLLAMA_TOP_P` | float | `0.9` | Top-p sampling parameter |
| `OLLAMA_TOP_K` | integer | `40` | Top-k sampling parameter |
| `OLLAMA_MAX_TOKENS` | integer | `2048` | Maximum tokens in response |
| `OLLAMA_SYSTEM_PROMPT` | string | `""` | System prompt for model |

### Model Pool Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MODEL_POOL_SIZE` | integer | `3` | Number of model instances |
| `MODEL_WARM_UP` | boolean | `true` | Pre-warm models on startup |
| `MODEL_CACHE_SIZE` | integer | `100` | Model response cache size |
| `MODEL_CACHE_TTL` | integer | `3600` | Cache TTL in seconds |

## Database Configuration

### SQLite Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | string | `"sqlite:///storage/database.sqlite"` | Database connection URL |
| `DATABASE_POOL_SIZE` | integer | `5` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | integer | `10` | Maximum pool overflow |
| `DATABASE_POOL_TIMEOUT` | integer | `30` | Pool connection timeout |
| `DATABASE_POOL_RECYCLE` | integer | `3600` | Connection recycle time |
| `DATABASE_ECHO` | boolean | `false` | Log SQL statements |
| `DATABASE_BACKUP_ENABLED` | boolean | `true` | Enable automatic backups |
| `DATABASE_BACKUP_INTERVAL` | integer | `24` | Backup interval in hours |
| `DATABASE_BACKUP_RETENTION` | integer | `7` | Backup retention in days |

### Migration Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MIGRATION_AUTO_RUN` | boolean | `false` | Auto-run migrations on startup |
| `MIGRATION_BACKUP_BEFORE` | boolean | `true` | Backup before migrations |
| `MIGRATION_VERIFY_INTEGRITY` | boolean | `true` | Verify database integrity |

## Redis Configuration

### Connection Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | string | `"redis://localhost:6379/0"` | Redis connection URL |
| `REDIS_PASSWORD` | string | `""` | Redis authentication password |
| `REDIS_DB` | integer | `0` | Redis database number |
| `REDIS_MAX_CONNECTIONS` | integer | `10` | Maximum connections |
| `REDIS_RETRY_ON_TIMEOUT` | boolean | `true` | Retry on timeout |
| `REDIS_HEALTH_CHECK_INTERVAL` | integer | `30` | Health check interval |

### Cache Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CACHE_TTL_DEFAULT` | integer | `3600` | Default cache TTL |
| `CACHE_TTL_SHORT` | integer | `300` | Short-term cache TTL |
| `CACHE_TTL_LONG` | integer | `86400` | Long-term cache TTL |
| `CACHE_KEY_PREFIX` | string | `"ai_nvcb"` | Cache key prefix |

## Security Configuration

### Authentication

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_SECRET_KEY` | string | *required* | JWT signing secret |
| `JWT_ALGORITHM` | string | `"HS256"` | JWT signing algorithm |
| `JWT_EXPIRATION_DELTA` | integer | `3600` | JWT expiration in seconds |
| `JWT_REFRESH_DELTA` | integer | `86400` | Refresh token expiration |
| `PASSWORD_MIN_LENGTH` | integer | `8` | Minimum password length |
| `PASSWORD_REQUIRE_SPECIAL` | boolean | `true` | Require special characters |
| `PASSWORD_REQUIRE_UPPERCASE` | boolean | `true` | Require uppercase letters |
| `PASSWORD_REQUIRE_NUMBERS` | boolean | `true` | Require numbers |

### Security Headers

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECURITY_HEADERS_ENABLED` | boolean | `true` | Enable security headers |
| `CSP_ENABLED` | boolean | `true` | Enable Content Security Policy |
| `CSP_REPORT_ONLY` | boolean | `false` | CSP report-only mode |
| `HSTS_ENABLED` | boolean | `true` | Enable HTTP Strict Transport Security |
| `HSTS_MAX_AGE` | integer | `31536000` | HSTS max age in seconds |

### CORS Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CORS_ENABLED` | boolean | `true` | Enable CORS |
| `CORS_ALLOW_ORIGINS` | list | `["http://localhost:8501"]` | Allowed origins |
| `CORS_ALLOW_METHODS` | list | `["GET", "POST", "PUT", "DELETE"]` | Allowed methods |
| `CORS_ALLOW_HEADERS` | list | `["*"]` | Allowed headers |
| `CORS_ALLOW_CREDENTIALS` | boolean | `true` | Allow credentials |

## File Upload and Storage

### Upload Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `UPLOAD_ENABLED` | boolean | `true` | Enable file uploads |
| `UPLOAD_MAX_SIZE` | integer | `10485760` | Max file size in bytes (10MB) |
| `UPLOAD_ALLOWED_TYPES` | list | `["jpg", "jpeg", "png", "gif", "pdf"]` | Allowed file types |
| `UPLOAD_FOLDER` | string | `"uploads"` | Upload directory path |
| `UPLOAD_VIRUS_SCAN` | boolean | `false` | Enable virus scanning |
| `UPLOAD_COMPRESS_IMAGES` | boolean | `true` | Compress uploaded images |
| `UPLOAD_GENERATE_THUMBNAILS` | boolean | `true` | Generate image thumbnails |

### Storage Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `STORAGE_TYPE` | enum | `"local"` | Storage backend: `local`, `s3`, `azure` |
| `STORAGE_LOCAL_PATH` | string | `"storage"` | Local storage path |
| `STORAGE_S3_BUCKET` | string | `""` | S3 bucket name |
| `STORAGE_S3_REGION` | string | `"us-east-1"` | S3 region |
| `STORAGE_S3_ACCESS_KEY` | string | `""` | S3 access key |
| `STORAGE_S3_SECRET_KEY` | string | `""` | S3 secret key |

## Performance and Caching

### Application Performance

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PERFORMANCE_MONITORING` | boolean | `true` | Enable performance monitoring |
| `RESPONSE_COMPRESSION` | boolean | `true` | Enable response compression |
| `STATIC_FILE_CACHING` | boolean | `true` | Enable static file caching |
| `DATABASE_QUERY_OPTIMIZATION` | boolean | `true` | Enable query optimization |
| `ASYNC_PROCESSING` | boolean | `true` | Enable async task processing |
| `MEMORY_LIMIT` | string | `"512MB"` | Memory limit per process |
| `CPU_LIMIT` | float | `1.0` | CPU limit per process |

### Connection Pooling

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HTTP_POOL_CONNECTIONS` | integer | `10` | HTTP connection pool size |
| `HTTP_POOL_MAX_SIZE` | integer | `20` | Maximum pool size |
| `HTTP_POOL_BLOCK` | boolean | `false` | Block when pool is full |
| `HTTP_TIMEOUT` | integer | `30` | HTTP request timeout |

## Rate Limiting

### API Rate Limits

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMITING_ENABLED` | boolean | `true` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | integer | `100` | Requests per time window |
| `RATE_LIMIT_WINDOW` | integer | `3600` | Time window in seconds |
| `RATE_LIMIT_BURST` | integer | `20` | Burst limit |
| `RATE_LIMIT_STORAGE` | enum | `"memory"` | Storage: `memory`, `redis` |

### Per-endpoint Limits

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RATE_LIMIT_GENERATE` | integer | `10` | Generation endpoint limit |
| `RATE_LIMIT_UPLOAD` | integer | `5` | Upload endpoint limit |
| `RATE_LIMIT_AUTH` | integer | `3` | Auth endpoint limit |

## Monitoring and Logging

### Logging Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | enum | `"INFO"` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | enum | `"json"` | Log format: `json`, `text` |
| `LOG_FILE_ENABLED` | boolean | `true` | Enable file logging |
| `LOG_FILE_PATH` | string | `"logs/app.log"` | Log file path |
| `LOG_FILE_MAX_SIZE` | integer | `10485760` | Max log file size (10MB) |
| `LOG_FILE_BACKUP_COUNT` | integer | `5` | Number of backup files |
| `LOG_ROTATION` | enum | `"time"` | Rotation: `time`, `size` |

### Structured Logging

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_STRUCTURED` | boolean | `true` | Enable structured logging |
| `LOG_CORRELATION_ID` | boolean | `true` | Include correlation IDs |
| `LOG_PERFORMANCE_METRICS` | boolean | `true` | Log performance metrics |
| `LOG_USER_ACTIONS` | boolean | `true` | Log user actions |
| `LOG_SENSITIVE_DATA` | boolean | `false` | Log sensitive data (dev only) |

### External Logging

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ELASTICSEARCH_ENABLED` | boolean | `false` | Enable Elasticsearch logging |
| `ELASTICSEARCH_HOST` | string | `"localhost:9200"` | Elasticsearch host |
| `ELASTICSEARCH_INDEX` | string | `"ai-nvcb-logs"` | Elasticsearch index |
| `SENTRY_ENABLED` | boolean | `false` | Enable Sentry error tracking |
| `SENTRY_DSN` | string | `""` | Sentry DSN |

### Metrics and Monitoring

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `METRICS_ENABLED` | boolean | `true` | Enable metrics collection |
| `PROMETHEUS_ENABLED` | boolean | `false` | Enable Prometheus metrics |
| `PROMETHEUS_PORT` | integer | `9090` | Prometheus metrics port |
| `HEALTH_CHECK_ENABLED` | boolean | `true` | Enable health checks |
| `HEALTH_CHECK_INTERVAL` | integer | `30` | Health check interval |

## Development and Testing

### Development Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEV_MODE` | boolean | `false` | Enable development mode |
| `DEV_AUTO_RELOAD` | boolean | `true` | Enable auto-reload |
| `DEV_DEBUGGER` | boolean | `false` | Enable debugger |
| `DEV_PROFILING` | boolean | `false` | Enable profiling |
| `DEV_MOCK_SERVICES` | boolean | `false` | Mock external services |
| `DEV_FAKE_DATA` | boolean | `false` | Use fake data generators |

### Testing Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TEST_DATABASE_URL` | string | `"sqlite:///test.db"` | Test database URL |
| `TEST_ASYNC_MODE` | boolean | `true` | Enable async testing |
| `TEST_COVERAGE` | boolean | `true` | Generate coverage reports |
| `TEST_PARALLEL` | boolean | `false` | Run tests in parallel |
| `TEST_TIMEOUT` | integer | `30` | Test timeout in seconds |

## Deployment Settings

### Docker Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCKER_IMAGE_TAG` | string | `"latest"` | Docker image tag |
| `DOCKER_REGISTRY` | string | `""` | Docker registry URL |
| `DOCKER_BUILD_TARGET` | enum | `"production"` | Build target |
| `DOCKER_MULTI_PLATFORM` | boolean | `false` | Multi-platform build |

### Container Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CONTAINER_NAME` | string | `"ai-nvcb"` | Container name |
| `CONTAINER_RESTART_POLICY` | enum | `"unless-stopped"` | Restart policy |
| `CONTAINER_MEMORY_LIMIT` | string | `"1G"` | Memory limit |
| `CONTAINER_CPU_LIMIT` | string | `"1.0"` | CPU limit |

### Kubernetes Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `K8S_NAMESPACE` | string | `"ai-nvcb"` | Kubernetes namespace |
| `K8S_REPLICAS` | integer | `3` | Number of replicas |
| `K8S_RESOURCES_REQUESTS_CPU` | string | `"100m"` | CPU requests |
| `K8S_RESOURCES_REQUESTS_MEMORY` | string | `"128Mi"` | Memory requests |
| `K8S_RESOURCES_LIMITS_CPU` | string | `"500m"` | CPU limits |
| `K8S_RESOURCES_LIMITS_MEMORY` | string | `"512Mi"` | Memory limits |

## External Services

### Email Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMAIL_ENABLED` | boolean | `false` | Enable email functionality |
| `EMAIL_SMTP_HOST` | string | `""` | SMTP server host |
| `EMAIL_SMTP_PORT` | integer | `587` | SMTP server port |
| `EMAIL_SMTP_USER` | string | `""` | SMTP username |
| `EMAIL_SMTP_PASSWORD` | string | `""` | SMTP password |
| `EMAIL_USE_TLS` | boolean | `true` | Use TLS encryption |
| `EMAIL_FROM_ADDRESS` | string | `""` | From email address |

### Notification Services

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `NOTIFICATIONS_ENABLED` | boolean | `false` | Enable notifications |
| `SLACK_WEBHOOK_URL` | string | `""` | Slack webhook URL |
| `DISCORD_WEBHOOK_URL` | string | `""` | Discord webhook URL |
| `TEAMS_WEBHOOK_URL` | string | `""` | Microsoft Teams webhook |

### Analytics

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ANALYTICS_ENABLED` | boolean | `false` | Enable analytics |
| `GOOGLE_ANALYTICS_ID` | string | `""` | Google Analytics ID |
| `MIXPANEL_TOKEN` | string | `""` | Mixpanel token |

## SSL/TLS Configuration

### Certificate Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SSL_ENABLED` | boolean | `false` | Enable SSL/TLS |
| `SSL_CERT_PATH` | string | `"ssl/cert.pem"` | Certificate file path |
| `SSL_KEY_PATH` | string | `"ssl/key.pem"` | Private key file path |
| `SSL_CA_PATH` | string | `""` | CA certificate path |
| `SSL_VERIFY_MODE` | enum | `"required"` | Verification mode |

### Let's Encrypt

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LETSENCRYPT_ENABLED` | boolean | `false` | Enable Let's Encrypt |
| `LETSENCRYPT_EMAIL` | string | `""` | Contact email |
| `LETSENCRYPT_DOMAINS` | list | `[]` | Domain list |
| `LETSENCRYPT_STAGING` | boolean | `true` | Use staging environment |

## Advanced Configuration

### Feature Flags

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `FEATURE_USER_REGISTRATION` | boolean | `true` | Allow user registration |
| `FEATURE_SOCIAL_LOGIN` | boolean | `false` | Enable social login |
| `FEATURE_API_VERSIONING` | boolean | `true` | Enable API versioning |
| `FEATURE_WEBHOOKS` | boolean | `false` | Enable webhook support |
| `FEATURE_BATCH_PROCESSING` | boolean | `true` | Enable batch processing |

### Experimental Features

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EXPERIMENTAL_AI_MODELS` | boolean | `false` | Enable experimental AI models |
| `EXPERIMENTAL_CACHING` | boolean | `false` | Enable experimental caching |
| `EXPERIMENTAL_COMPRESSION` | boolean | `false` | Enable experimental compression |

## Environment-Specific Examples

### Development (.env.development)
```bash
DEBUG=true
DEV_MODE=true
DEV_AUTO_RELOAD=true
LOG_LEVEL=DEBUG
OLLAMA_HOST=http://localhost:11434
DATABASE_ECHO=true
CORS_ALLOW_ORIGINS=["http://localhost:8501", "http://localhost:3000"]
```

### Staging (.env.staging)
```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
SSL_ENABLED=true
BACKUP_ENABLED=true
HEALTH_CHECK_ENABLED=true
RATE_LIMITING_ENABLED=true
```

### Production (.env.production)
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
SSL_ENABLED=true
SECURITY_HEADERS_ENABLED=true
RATE_LIMITING_ENABLED=true
PROMETHEUS_ENABLED=true
BACKUP_ENABLED=true
DATABASE_BACKUP_ENABLED=true
LETSENCRYPT_ENABLED=true
```

## Configuration Validation

Use the built-in configuration validator:

```bash
# Validate current configuration
poetry run python -c "from utils.config import validate_config; validate_config()"

# Check specific environment
poetry run python -c "from utils.config import validate_config; validate_config('production')"

# Generate configuration report
poetry run python -c "from utils.config import config_report; print(config_report())"
```

## Troubleshooting

### Common Issues

1. **Invalid boolean values**: Use `true`/`false`, not `True`/`False` or `1`/`0`
2. **List format**: Use JSON array format: `["item1", "item2"]`
3. **URL format**: Ensure proper protocol and format
4. **File paths**: Use forward slashes or properly escaped backslashes
5. **Sensitive data**: Never commit real secrets to version control

### Validation Commands

```bash
# Test database connection
poetry run python -c "from utils.database import test_connection; test_connection()"

# Test Redis connection
poetry run python -c "from utils.cache import test_redis; test_redis()"

# Test Ollama connection
poetry run python -c "from utils.ai import test_ollama; test_ollama()"

# Validate all configurations
poetry run python -m utils.config_validator
```

## Security Best Practices

1. **Use strong secret keys**: Generate with `openssl rand -hex 32`
2. **Enable all security features** in production
3. **Regularly rotate secrets**
4. **Use environment-specific configurations**
5. **Enable logging and monitoring**
6. **Keep dependencies updated**
7. **Use SSL/TLS in production**
8. **Enable rate limiting**
9. **Configure proper CORS settings**
10. **Use secure headers**

For more information, see the main [README.md](../README.md) and [Security Guide](SECURITY.md).

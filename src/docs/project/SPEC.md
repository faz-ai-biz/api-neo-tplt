# File Explorer API v1.0 (Merged Revision)
**official docs**
**version** 0.0.1

This document provides a **rebased** and **consolidated** version of the File 
Explorer API specification at **version 1.0**. It incorporates recent feedback 
and new feature requests, along with a **requirements classification** 
(_Must Have_, _Should Have_, _Nice to Have_) for each new or existing feature.


---

## Overview

A secure, **read-only** File Explorer API built with Flask on Linux environments. This version (**v1.0**) strengthens security, enforces standardized response formats, and outlines robust rate limiting. It also provides optional features (like **batch operations**, **compressed directory downloads**, and more) to improve usability and performance in multi-user scenarios.

> **Note**:
> 
> - **All references** to generating JWT tokens are out of scope for this specification. We assume tokens are acquired from a **separate microservice** adhering to standard JWT best practices (Bearer tokens, refresh tokens, etc.).
> - The endpoints in this spec strictly handle **read** operations (no write/delete operations are provided).

---

## Requirements Classification

Below is the classification of **new and existing** requirements into **Must Have**, **Should Have**, and **Nice to Have**.

### Must Have

10. **JWT-based Authentication** (RS256, mandatory claims).
11. **Path Traversal Protection** (must remain within base directory).
12. **File Type Validation** for text-only content endpoints.
13. **Rate Limiting** (global and per-endpoint).
14. **CORS** control and TLS 1.2+.
15. **User-specific base path** (if multi-user isolation is required).

### Should Have

16. **Batch Metadata Endpoints** (for efficiency).
17. **File Type Filtering** in directory listings (reduce clutter, strengthen security).
18. **Compressed Directory Downloads** (tar/gzip, zip, etc.).
19. **ETag-based caching** support.
20. **Cursor-based Pagination**.

### Nice to Have

21. **Webhook Support** for long-running searches.
22. **Subscriptions / WebSocket** for directory change notifications.
23. **Optional .gitignore** or ignore-file support in the tree endpoint.
24. **Search in file content** with advanced features (e.g., partial match highlights).

---

## Global Standards

### Authentication

- The **File Explorer API** expects a valid **JWT** in the `Authorization: Bearer <token>` header.
- **JWT Algorithm**: RS256 only.
- **JWT Claims** (minimum):
    - `iat` (Issued At)
    - `exp` (Expiry)
    - `sub` (Subject, e.g., username or user ID)
    - `scope` (List of scopes/roles for RBAC checks)
- **Access Tokens** typically valid for **1 hour**.
- **Refresh Tokens** (24 hours or more) are managed by an external auth service.

> **Important**:  
> **No** endpoints in this spec are provided for **creating** or **refreshing** tokens. That is delegated to an **authentication microservice**.

### Rate Limiting

A **global** limit of **1000 requests** per IP per hour, plus **per-endpoint** limits. Responses **must** include:

- **X-RateLimit-Limit**
- **X-RateLimit-Remaining**
- **X-RateLimit-Reset**

> **Recommended Per-Endpoint Limits**:

|**Endpoint/Category**|**Limit**|
|---|---|
|**/api/v1/files** (metadata)|200/min|
|**/api/v1/files/content**|150/min + 750/min per IP (recommended)|
|**/api/v1/files/download**|20/min|
|**/api/v1/files/batch**|100/min|
|**/api/v1/directories**|100/min + 500/min per IP|
|**/api/v1/directories/tree**|20/min|
|**/api/v1/search**|25/min + 5/10sec + 100/min per IP|
|**/api/v1/system/health**|60/min|
|**/api/v1/me**|60/min|
|**/api/v1/me/base-path**|10/min|

### Security

25. **TLS 1.2 or higher** is required.
26. **Path Traversal Protection**: Must ensure requests remain within base path.
27. **File Type Validation**: Validate **magic number** or extension checks for content reads.
28. **Symbolic Links**: Configurable to follow or ignore.
29. **CORS**: Admin-configurable allowed origins.
30. **Request Body Size**: Max **1MB** for JSON-based endpoints.
31. **Security Headers** (recommended):
    - `X-Content-Type-Options: nosniff`
    - `X-Frame-Options: DENY`
    - `Strict-Transport-Security: max-age=63072000`
32. **Checksum Algorithm**: **SHA-256** recommended for file metadata.
33. **Sensitive Paths**: Deny-list for restricted directories (e.g., `/etc`).

### Response Standards

All JSON responses must include:

```json
{
  "requestId": "UUID",
  "timestamp": "ISO 8601 UTC",
  "apiVersion": "1.0",
  ...
}
```

#### Pagination

- **Cursor-based**.
- **Default**: 50 items/page.
- **Max**: 200 items/page.
- **Cursor Format**: Implementation-defined but must be **URL-safe**.

#### ETag and Caching

- Endpoints **should** return `ETag` headers when feasible (directory listings, file metadata).
- **If-None-Match** or **If-Match** can reduce redundant data transfer.

#### Error Format

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object or null",
    "requestId": "UUID",
    "timestamp": "ISO 8601"
  }
}
```

---

## Endpoints

> **JWT is mandatory** for **all** endpoints in this API.

### 1. File Operations

#### 1.1 Get File Metadata

```
GET /api/v1/files
```

- **Query Param**: `path` (required)
- **Response**:
    
    ```json
    {
      "metadata": {
        "name": "string",
        "path": "string",
        "size": 123,
        "mimeType": "string",
        "modified": "ISO 8601",
        "created": "ISO 8601",
        "checksum": "SHA-256 hash",
        "permissions": {
          "readable": true
        }
      }
    }
    ```
    
- **Max Rate**: 200/minute
- **ETag**: Should be included if feasible.

#### 1.2 Get File Content

```
GET /api/v1/files/content
```

- **Query Params**:
    - `path` (required)
    - `encoding` (optional, default: `utf-8`)
- **Headers**:
    - `Accept: text/plain`
- **Response**:
    - `Content-Type: text/plain`
    - **Raw** file content (for text files)
- **Restrictions**:
    - Max file size: **5MB**
    - Must be **text** (validated by magic number)
- **Rate Limit**: ~150/min

#### 1.3 Download File

```
GET /api/v1/files/download
```

- **Query Params**:
    - `path` (required)
    - `compression` (optional): `gzip`, `zstd`
- **Headers**:
    - `Range: bytes=start-end` (optional)
- **Response**:
    - `Content-Type: application/octet-stream`
    - `Content-Disposition: attachment; filename="<fileName>"`
    - If partial content: `Content-Range: bytes start-end/total`
- **Restrictions**:
    - Max file size: **100MB**
- **Rate Limit**: 20/min
- **Streaming** recommended (e.g., 4MB chunks).

---

### 2. **Batch Operations** (Should Have)

To efficiently retrieve **metadata** for **multiple files** or **multiple directories** at once, a new endpoint is introduced:

```
POST /api/v1/files/batch
```

- **Request Body**:
    
    ```json
    {
      "paths": [
        "string",  // e.g., "docs/report.txt"
        "string"   // e.g., "docs/image.png"
      ]
    }
    ```
    
- **Response**:
    
    ```json
    {
      "results": [
        {
          "path": "string",
          "exists": true,
          "metadata": {
            "name": "string",
            "size": 123,
            "mimeType": "string",
            "modified": "ISO 8601",
            "checksum": "SHA-256 hash"
          },
          "error": null
        },
        {
          "path": "string",
          "exists": false,
          "metadata": null,
          "error": {
            "code": "FILE001",
            "message": "File not found"
          }
        }
      ]
    }
    ```
    
- **Restrictions**:
    - Up to **50** paths per request (configurable).
- **Rate Limit**: 100/min

> **Usage**: Allows clients to fetch multiple file metadata records in a single call.

---

### 3. Directory Operations

#### 3.1 List Directory Contents

```
GET /api/v1/directories
```

- **Query Params**:
    - `path` (required)
    - `cursor` (optional)
    - `limit` (optional, default: 50, max: 200)
    - `showHidden` (optional, default: false)
    - `sortBy` (optional: name|size|modified)
    - `sortOrder` (optional: asc|desc)
    - `fileTypeFilter` (optional, e.g., `image`, `video`, `pdf`) **(Should Have)**
- **Response**:
    
    ```json
    {
      "entries": [
        {
          "name": "string",
          "type": "file|directory",
          "size": 123,
          "modified": "ISO 8601",
          "permissions": {
            "readable": true
          }
        }
      ],
      "pagination": {
        "nextCursor": "string or null",
        "hasMore": true
      }
    }
    ```
    
- **Rate Limit**: 100/min

> **File Type Filtering**:
> 
> - This is a **Should Have** feature that uses either MIME type checks or extension-based matching.
> - Example usage: `GET /api/v1/directories?path=photos&fileTypeFilter=image`

#### 3.2 Get Directory Tree

```
GET /api/v1/directories/tree
```

- **Query Params**:
    - `path` (required)
    - `excludePatterns` (optional) e.g., `["*.git", "*.tmp"]`
    - `maxDepth` (optional, default: 10)
- **Response**:
    
    ```json
    {
      "entries": [
        {
          "path": "string",
          "type": "file|directory",
          "size": 123,
          "modified": "ISO 8601"
        }
      ]
    }
    ```
    
- **Restrictions**:
    - Max entries: **10,000**
- **Rate Limit**: 20/min

#### 3.3 (Future) Compressed Directory Download (Should Have)

A new endpoint could allow clients to download an **entire directory** as a compressed archive (e.g., `.zip`, `.tar.gz`):

```
GET /api/v1/directories/download
```

- **Query Params**:
    - `path` (required)
    - `format` (optional, default: `zip` or `tar.gz`)
- **Response**:
    - `Content-Type: application/octet-stream`
    - The archive containing the directory’s contents
- **Restrictions**:
    - Entire directory must be under the max file size limit (configurable, e.g., 100MB or 1GB).
    - **Streaming** recommended.

_(Implementation details left to each deployment scenario.)_

---

### 4. Search

#### 4.1 Search Files and Directories

```
GET /api/v1/search
```

- **Query Params**:
    - `query` (required)
    - `basePath` (optional)
    - `searchIn`: `name|content`
    - `caseSensitive`: (optional, default: false)
    - `cursor`: (optional)
    - `limit`: (default: 50, max: 200)
    - `filePattern`: (optional)
    - `timeout`: (optional, default: 30s)
    - `mimeFilter`: (optional) e.g., `text/plain`, `application/json`
- **Response**:
    
    ```json
    {
      "results": [
        {
          "path": "string",
          "type": "file|directory",
          "matches": [
            {
              "line": 10,
              "content": "string",
              "highlights": [
                {
                  "start": 5,
                  "end": 15
                }
              ]
            }
          ]
        }
      ],
      "pagination": {
        "nextCursor": "string or null",
        "hasMore": true
      }
    }
    ```
    
- **Restrictions**:
    - Max search depth: **10** directories from `basePath`
    - Max file size for content search: **10MB**
    - Timeout: **30s** default
- **Rate Limit**: ~25/min

##### (Nice to Have) Webhook for Long-Running Searches

- **Webhook** or **async** callback for queries that may exceed standard timeouts.
- **Client** provides a callback URL, the server posts partial or final results to the webhook.

_(Exact spec left to implementers.)_

---

### 5. System

#### 5.1 Health Check

```
GET /api/v1/system/health
```

- **Response**:
    
    ```json
    {
      "status": "healthy|degraded|unhealthy",
      "version": "string",
      "timestamp": "ISO 8601",
      "checks": {
        "filesystem": {
          "status": "up|down",
          "latency": 123
        },
        "memory": {
          "status": "ok|warning|critical",
          "used": 123456,
          "total": 789000
        },
        "storage": {
          "total": 104857600,
          "used": 52428800,
          "available": 52428800
        }
      }
    }
    ```
    
- **Rate Limit**: 60/min

---

### 6. **User Profile / Per-User Base Path**

> _Must Have if the API is multi-tenant or user-aware._

#### 6.1 Get Current User Profile

```
GET /api/v1/me
```

- **Response**:
    
    ```json
    {
      "requestId": "UUID",
      "timestamp": "ISO 8601",
      "apiVersion": "1.0",
      "username": "string",
      "basePath": "string",
      "additionalInfo": {
        "email": "string",
        "quota": "number or null",
        "lastLogin": "ISO 8601 or null"
      }
    }
    ```
    
- **Rate Limit**: 60/min

#### 6.2 Set or Update User Base Path

```
PUT /api/v1/me/base-path
```

- **Request Body**:
    
    ```json
    {
      "basePath": "string"
    }
    ```
    
- **Constraints**:
    - Must start with `/home/` or similar user-home pattern.
    - Must match the user’s identity (subfolder checks).
    - The path must exist (or be creatable).
- **Response**:
    
    ```json
    {
      "requestId": "UUID",
      "timestamp": "ISO 8601",
      "apiVersion": "1.0",
      "basePath": "string"
    }
    ```
    
- **Rate Limit**: 10/min

> **All file/directory calls** for this user are then restricted to the updated `basePath`.

---

## Future or Optional Enhancements

34. **Directory Change Subscription** (Nice to Have):
    - WebSockets or SSE to notify when changes occur in a directory.
35. **Extended Search Functionality**:
    - Fuzzy matching, synonyms, advanced filters.
36. **Delta Sync / Checkpointing**:
    - For large directories, provide incremental updates.

---

## Error Codes

|**Code**|**Meaning**|
|---|---|
|**AUTH001**|Invalid credentials (if relevant when verifying tokens)|
|**AUTH002**|Token expired|
|**AUTH003**|Invalid token|
|**AUTH004**|Insufficient permissions|
|**FILE001**|File not found|
|**FILE002**|File too large|
|**FILE003**|Invalid file type|
|**FILE004**|Path traversal attempted|
|**DIR001**|Directory not found|
|**DIR002**|Not a directory|
|**SEARCH001**|Invalid search pattern|
|**SEARCH002**|Search timeout|
|**SYS001**|System overloaded (define threshold triggers)|
|**SEC001**|Invalid security header configuration|
|**SEC002**|Request body size exceeded|
|**PAG001**|Invalid cursor format|

---

## Implementation Guidelines

### Security Considerations

37. Enforce **JWT** validation at all endpoints.
38. **Rate limiting** at gateway or application level.
39. **Log** security events (auth failures, path traversal attempts, excessive request rejections).
40. Use **dependency** auditing tools (e.g., `pip-audit`).
41. Maintain a **revocation list** for tokens if necessary.

### Environment Variables

```bash
# Required
BASE_PATH="/absolute/path/to/serve"      # Default root if not user-based
JWT_PUBLIC_KEY="/path/to/jwt_pub.pem"    # For RS256 verification
JWT_PRIVATE_KEY="/path/to/jwt_priv.pem"  # Not used if verifying only

# Optional
TOKEN_REVOCATION_CHECK_INTERVAL=300      # seconds
MAX_SEARCH_TIMEOUT=30                    # seconds
FILE_STREAM_CHUNK_SIZE=4194304           # 4MB
```

### Performance Optimization

- **Cache File Metadata**: e.g., 30s caching for popular directories.
- **Efficient FS Traversal**: OS-level calls or specialized libraries.
- **Request Timeouts**: Kill requests exceeding a threshold (e.g., 60s).
- **Large File Streaming**: Serve files in chunks to avoid memory spikes.

### Monitoring Requirements

- Track **request latency** (P95, P99), **error rates**, **rate limit usage**, **search performance**, and **auth failures**.
- **File system capacity**: Monitor usage vs. total capacity.

### Testing Requirements

- **Unit Tests**: 90% coverage min.
- **Integration Tests**: Validate each endpoint with good/bad input.
- **Load Testing**: Ensure stable performance under concurrency.
- **Security Penetration**: Check path traversal, injection, token forgery.
- **Edge Cases**: Very large directories, near-limit file sizes, unusual file types.
- **Search Timeout**: Return `SEARCH002` appropriately.

---

## Structural & Future Recommendations

42. **Architectural Diagrams**: Show sequence flows for file requests, security checks, user base path logic.
43. **Deprecation Policy**: If any older versions exist, define how long they’ll be supported.
44. **Versioning & Backward Compatibility**: This is **v1.0**. Use minor versions (v1.1) for small changes.
45. **Define “System Overloaded”** (SYS001) with CPU, memory, or queue thresholds.

---

## Example Secure File Access Flow

```python
def handle_file_request(request):
    try:
        # 1. Validate JWT (bearer token in Authorization header)
        token = get_bearer_token(request.headers)
        token_data = validate_jwt(token)  # RS256, check exp, iat, scope

        # 2. Check user base path (e.g., from DB)
        user_base_path = get_user_base_path(token_data["sub"])  # e.g. /home/alice

        # 3. Resolve requested path
        raw_path = request.args["path"]
        sanitized_rel_path = sanitize_path(raw_path)
        abs_path = (Path(user_base_path) / sanitized_rel_path).resolve()

        # 4. Ensure path within allowed base
        if not abs_path.is_relative_to(user_base_path):
            raise SecurityException("Path traversal attempt", code="FILE004")

        # 5. Check file existence & read permissions
        if not abs_path.exists():
            raise FileNotFoundError("File not found", code="FILE001")
        if not os.access(abs_path, os.R_OK):
            raise SecurityException("Insufficient permissions", code="AUTH004")

        # 6. Return or stream the file content
        return stream_file(abs_path)

    except SecurityException as se:
        log_security_event(se)
        return error_response(403, se.code, str(se))
    except FileNotFoundError as fe:
        return error_response(404, fe.code, str(fe))
    ...
```

---

### **Conclusion**

The **File Explorer API v1.0** is a secure, extensible solution for **read-only** 
file system exploration. It mandates strong security measures (JWT + path containment), 
supports efficient batch and streaming operations, and provides robust rate 
limiting and monitoring. While many features are **must have** for production 
readiness, additional **should have** and **nice to have** enhancements can 
further improve developer and end-user experience.
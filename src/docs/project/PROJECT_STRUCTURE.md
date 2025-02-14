## 📁 File System Structure

### File Service Design
The project uses a base path approach for file operations to ensure security and proper isolation:

```
/app/                           # Application root
├── data/                      # Data directory
│   ├── uploads/              # User uploads
│   ├── exports/             # Generated exports
│   └── temp/                # Temporary files
```

### Security Considerations
- Each FileService instance requires an explicit base path
- No global file storage path is defined to enforce explicit path declarations
- Path traversal protection is implemented at the service level
- All file operations are contained within their designated base paths

### Usage Example
```python
# Initialize with specific base path
file_service = FileService(base_path=Path("/app/data/uploads"))

# Operations are restricted to this base path
contents = file_service.list_directory("subfolder")  # Will list /app/data/uploads/subfolder
```

### Best Practices
1. Always specify explicit base paths for file operations
2. Use separate base paths for different types of files (uploads, exports, etc.)
3. Consider cleanup strategies for temporary files
4. Implement appropriate access controls for different file areas 
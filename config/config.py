import os
from typing import Optional
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务器配置
    server_host: str = "0.0.0.0"
    server_port: int = 8002
    server_reload: bool = True
    
    # 临时文件目录
    temp_dir: str = "temp_uploads"
    
    # 最大文件上传大小 (bytes) - 10MB
    max_upload_size: int = 10 * 1024 * 1024
    
    # API配置
    api_prefix: str = "/api"
    
    class Config:
        env_file = ".env"

settings = Settings()
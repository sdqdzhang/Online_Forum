# app/core/config.py
from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# 定义配置类，继承 BaseSettings
class Settings(BaseSettings):

    # 1. 数据库 URL：定义类型+默认值（如果.env里没有，就用默认值）
    database_url: str
    # 2. JWT 密钥：字符串类型
    secret_key: str = "default-secret-key-for-dev-only"
    # 3. Token 过期时间：整数类型，比如默认30分钟
    access_token_expire_minutes: int = 30  # 给个默认值更健壮
    algorithm: str
    project_name:str
    debug: bool
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"
    cache_ttl_seconds: int = 300
    cache_logical_expire_seconds: int = 180
    cache_lock_seconds: int = 10
    hot_rank_key: str = "hot:posts"
    # 常驻连接数
    DB_POOL_SIZE : int = 10
    # 峰值临时连接数
    DB_MAX_OVERFLOW : int = 20
    # 连接回收时间（秒）
    DB_POOL_RECYCLE : int = 3600

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # 指定.env文件路径
        env_file_encoding="utf-8",  # 编码格式
        case_sensitive=False,  # 不区分配置项大小写
        extra="ignore"  # 忽略.env中未定义的配置项（可选，增强健壮性）
    )


# 创建配置实例，整个项目都可以导入这个实例使用配置
settings = Settings()

# 测试代码（可选，运行config.py看看是否能正确读取）
if __name__ == "__main__":
    print("项目根目录:", BASE_DIR)
    print("数据库URL:", settings.database_url)
    print("JWT密钥:", settings.secret_key)
    print("Token过期时间（分钟）:", settings.access_token_expire_minutes)
    print("debug", settings.debug)
    print("algorithm", settings.algorithm)
    print("projname", settings.project_name)
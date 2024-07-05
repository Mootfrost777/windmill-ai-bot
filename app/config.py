from pydantic_settings import BaseSettings


class Config (BaseSettings):
    token: str
    db_url: str
    images_dir: str
    ml_path: str


config = Config(_env_file='.env')

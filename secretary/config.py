from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    master_number: str = "+10000000000"
    database_path: str = "secretary.db"
    master_name: str = "Master"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            master_number=os.getenv("MASTER_NUMBER", "+10000000000"),
            database_path=os.getenv("DATABASE_PATH", "secretary.db"),
            master_name=os.getenv("MASTER_NAME", "Master"),
        )

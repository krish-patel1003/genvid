from enum import Enum

class VideoStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    PROCESSING = "PROCESSING"
    READY = "READY"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"
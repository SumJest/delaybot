import smart_getenv

VK_TOKEN = smart_getenv.getenv("VK_TOKEN", type=str)
VK_GROUP_ID = smart_getenv.getenv("VK_GROUP_ID", type=int)

MAX_USER_GROUPS = smart_getenv.getenv("MAX_USER_GROUPS", type=int, default=5)
import json

config = {
    "service": {
        "daily-report": {
            "login": "https://weixine.ustc.edu.cn/2020/caslogin",
            "url": "https://weixine.ustc.edu.cn/2020/home",
            "exec": "https://weixine.ustc.edu.cn/2020/daliy_report",
        },
        "daily-apply": {
            "login": "https://weixine.ustc.edu.cn/2020/caslogin",
            "url": "https://weixine.ustc.edu.cn/2020/apply/daliy",
            "pre-exec": "https://weixine.ustc.edu.cn/2020/apply/daliy/i",
            "exec": "https://weixine.ustc.edu.cn/2020/apply/daliy/post",
        }
    }
}

def DumpConfig(stuid, user_config):
    with open(f"conf/{stuid}.json", "w") as f:
        json.dump(user_config, f, indent=4)

def LoadConfig(stuid):
    try:
        with open(f"conf/{stuid}.json", "r") as f:
            user_config = json.load(f)
    except Exception as e:
        user_config = {}
    return user_config
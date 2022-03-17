from login import Login
from report import Report

from config import config

if __name__ == "__main__":
    for service, detail in config["service"].items():
        print(f"{service}: {detail['url']}")
    # print("service:\n", config["service"])
    service = input("Choose service:")
    login = Login(service=config["service"][service]["login"])
    if service == Report.SERVICE_NAME:
        report = Report(session=login.session)

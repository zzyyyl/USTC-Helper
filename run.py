from login import Login
from report import Report
from apply import Apply
from config import config
from _argparse import ArgParser, ArgConflictCheck, ArgInit

if __name__ == "__main__":
    args = ArgParser().parse_args()
    ArgConflictCheck(args)
    ArgInit(args)
    
    if args.daily:
        login = Login(service="daily-report",
                      stuid=args.stuid, store_password=args.store_password, silence=args.silence)
        report = Report(session=login.session, stuid=login.stuid, silence=args.silence)
        _apply = Apply(session=login.session, stuid=login.stuid, silence=args.silence)
    elif args.service:
        service = args.service
        login = Login(service=service,
                      stuid=args.stuid, store_password=args.store_password, silence=args.silence)

        if service == Report.SERVICE_NAME:
            report = Report(session=login.session, stuid=login.stuid, silence=args.silence)
        elif service == Apply.SERVICE_NAME:
            _apply = Apply(session=login.session, stuid=login.stuid, silence=args.silence)
    else:
        for service, detail in config["service"].items():
            print(f"{service}: {detail['url']}")
        while True:
            service = input("Choose service:")
            if service not in config["service"]:
                break
            login = Login(service=service,
                      stuid=args.stuid, store_password=args.store_password, silence=args.silence)

            if service == Report.SERVICE_NAME:
                report = Report(session=login.session, stuid=login.stuid, silence=args.silence)
            elif service == Apply.SERVICE_NAME:
                _apply = Apply(session=login.session, stuid=login.stuid, silence=args.silence)
            else:
                break
    if not args.silence:
        print("Exit.")

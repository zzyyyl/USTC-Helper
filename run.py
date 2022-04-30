import traceback
from USTCHelper import config
from _argparse import ArgParser, ArgConflictCheck, ArgInit
from USTCHelper import Login
from USTCHelper import seParams

def run_service(args, service):
    global config
    service, params = seParams(service)
    if service not in config["service"]:
        raise RuntimeError(f"service `{service}` does not exist.")

    login = Login(
        service=service,
        stuid=args.stuid,
        store_password=args.store_password,
        silence=args.silence
    )

    return config["service"][service]["entry"](
        session=login.session,
        stuid=login.stuid,
        silence=args.silence,
        params=params
    )

if __name__ == "__main__":
    args = ArgParser().parse_args()
    ArgConflictCheck(args)
    ArgInit(args)
    
    if args.daily:
        run_service(args, 'daily-report')
        run_service(args, 'daily-apply')
    elif args.service:
        run_service(args, args.service)
    else:
        for service, detail in config["service"].items():
            if 'doc' in detail:
                doc_info = ": " + detail['doc']
            else:
                doc_info = ''
            if 'url' in detail:
                url_info = ", url=" + detail['url']
            else:
                url_info = ''
            print(f"{service}{doc_info}{url_info}")
        while True:
            service = input(">>> ")
            if service == "exit":
                break;
            try:
                run_service(args, service)
            except Exception as e:
                traceback.print_exc()
    if not args.silence:
        print("Bye")

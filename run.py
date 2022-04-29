from USTCHelper import config
from _argparse import ArgParser, ArgConflictCheck, ArgInit
from USTCHelper import Login

def run_service(args, service=None, params=None):
    global config
    if not service:
        try:
            service = args.service
            assert service
        except Exception as e:
            raise
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
        run_service(args)
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
            service = input(">>> ").split(' ', 1)
            if service[0] not in config["service"]:
                break
            if len(service) == 1:
                run_service(args, service[0])
            else:
                run_service(args, service[0], params=service[1])
    if not args.silence:
        print("Bye")

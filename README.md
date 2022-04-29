# USTC-Helper

[中文](/README-cn.md)

**This project is for learning and communication purposes only. The developer is not responsible for any problems caused by the use of this script, does not guarantee the effectiveness of this script, and in principle does not provide any form of technical support.**

Suggestions for improvements to this project are welcome.

**Warning:**

- The error handling in this project is not perfect, please try to make sure your configuration is error free.
- As the api of the health report website changes frequently, there is no guarantee that the script is up to date.

Usage:

- `pip install -r requirements.txt`
- Run `python run.py`

The first time you use it you need to enter the user configuration.
It can also take some command line arguments, you can use `run.py -h` to learn more.

**Notes:**

- Your user configuration will be saved in `conf/`, you can check your configuration in the corresponding file. You can delete the file in `conf/` to reset your configuration.

## Feature

You can use a feature by typing the name of it in the table below after running.

Alternatively, you can specify the feature to be used with the command line parameter `-service SERVICE`.

|Feature|Name|
|:---:|:---:|
|Daily health reporting|`daily-report`|
|Out-of-school reporting|`daily-apply`|
|Check class schedule|`lesson-table`|

**Notes:**

1. The default residence is in Central Campus, please modify the `params` in the `report.py` file if you need.
2. There may be some bugs in the `apply.py` file if the report parameters are not `3`.

### Check class schedule

Usage:

- `lesson-table [DATE [TIME]]`

The format of `DATE` can be the following (case-insensitive).

1. `today|tomorrow`
2. `(thisweek|nextweek|next-?[0-9]+week) (mon|tue|wed|thr|fri|sat|sun)`
   denotes `weekday of (this week|next week|next n weeks)`.
   For example, `next-1week Mon` denotes `last Monday`.
3. `(thisweek|nextweek|next-?[0-9]+week) (-? [0-9]+)`
   means `m days past Monday of (thisweek|nextweek|next n week)`.
   For example, `thisweek -2` denotes `last Saturday` (2 days to this Monday).
4. a date in the form of `YYYY-MM-DD`, `YY-MM-DD`, `MM-DD`

The format of `TIME` can be as follows.

1. time in the form of `HH:MM:SS`, `HH:MM`

**Note:**

- Please do not enter extra spaces.

### Auto-run (Action)

This feature integrates both daily health reporting and out-of-school reporting.

You can fork and configure the parameters `USERNAME` and `CONFIG` in your secrets. Where:

- `USERNAME` is your username;
- `CONFIG` is the base64 format of your json configuration, you can find it in `conf/{USERNAME}.json` or via `get-config` after execution.

**Note that base64 is not an encryption algorithm, so please keep your personal information safe.**

The parameters, when not encoded in base64, are similar to the following example.

``` python
ORIGIN_CONFIG = {
    "user_params": {
        "daily-report": {
            "dorm_building": "1",
            "dorm": "1234",
            "jinji_lxr": "Zhang San",
            "jinji_guanxi": "Father",
            "jiji_mobile": "1234567890"
        },
        "daily-apply": {
            "t": "3",
            "return_college[]": [
                "东校区",
                "西校区",
                "南校区",
                "北校区",
                "中校区"
            ],
            "reason": "course"
        }
    },
    "password": "PAS5W0RD"
}
```

You can use

```python
CONFIG = base64.b64encode(json.dumps(ORIGIN_CONFIG).encode('gbk')).decode("ASCII")
```

to get the base64 encoded `CONFIG`.

It is recommended to check the correctness of your `CONFIG` once to avoid submitting wrong information. You can use

```python
json.loads(base64.b64decode(CONFIG.encode()).decode('gbk'))
```

and compare it with `ORIGIN_CONFIG`.

# USTC 助手

这是一个为了方便同学们在科大生活的项目。

使用方法：

- `pip install -r requirements.txt`
- 在 `config.py` 中填写你的配置
- 运行 `python run.py` 

首次使用时需要输入用户名和密码。系统配置会自动生成为 `config.json` 文件，用户配置在 `config.py` 文件中手动修改。

*Tips: 若不想保存系统配置，可以手动删除每次生成的 `config.json` 文件。*

## 功能

目前仅支持 daily-report 一个功能，即每日健康上报。

### 每日健康上报 ( daily-report )

你可以在运行 `run.py` 后输入 `daily-report` 来使用这个功能。


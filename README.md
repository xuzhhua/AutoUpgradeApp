# AutoUpgradeApp.py

**其他语言版本 / Other Languages / 他の言語版:**
- [English](README_EN.md)
- [日本語](README_JA.md)

本脚本用于自动检查并升级 Windows 应用（基于 Windows 包管理器 winget）。  
支持多语言输出、用户自定义排除和强制更新列表，并记录更新活动。  
脚本设计为持续运行，每24小时检查一次更新。

## 模块说明

- `subprocess`：运行 winget 命令
- `time`：定时周期性检查
- `os`：文件与路径操作
- `keyboard`：更新前后发送快捷键
- `datetime`：记录更新时间戳
- `unicodedata`：处理多语言字符显示宽度
- `json`：加载语言包
- `locale`：检测系统语言

## 主要函数

- **load_lang_pack()**  
  从 `lang.json` 加载语言包，依据系统语言返回本地化字符串字典。

- **get_default_excluded_apps()**  
  返回默认排除的应用名和表头列表。

- **load_excluded_apps(file_path)**  
  从文件加载排除和强制更新列表，返回两个列表。

- **check_and_update_apps()**  
  使用 winget 检查可用更新。  
  跳过排除列表中的应用（除非在强制更新列表中），执行更新并记录结果。  
  **新功能：实时显示winget升级过程的输出信息。**

- **substr_by_display_width(s, start, length)**  
  按显示宽度截取字符串，兼容宽字符。

- **get_display_width(s)**  
  计算字符串的显示宽度，考虑宽字符。

- **monitor_updates()**  
  主循环，每24小时触发一次更新检查。  

- **get_current_datetime_string()**  
  返回当前日期和时间的格式化字符串。

## 使用方法

1. 直接运行脚本，开始持续自动更新监控。
2. 将 `lang.json`、`update_policy.txt`、`proxy.txt`（可选）和 `check_interval.txt`（可选）放在同一目录下，用于语言、排除配置、代理设置和检查间隔配置。

## 注意事项

1. 确保安装了 winget，并已配置好环境变量。
2. 运行脚本需要管理员权限，以便执行更新操作。
3. 根据需要调整 `update_policy.txt`、`lang.json`、`proxy.txt` 和 `check_interval.txt` 文件中的内容。
   特别是lang.json里英文与日文版的titles和all_latest的设定由于系统限制未经测试，请自行修改。
4. 运行脚本时请保持网络连接，以便下载更新。
5. 如果在中国大陆使用，可能需要使用魔法。

## update_policy.txt 使用说明

- 每行填写一个要排除自动更新的应用名称（可为ID、显示名等，支持模糊匹配，忽略大小写）。
- 以英文感叹号 `!` 开头的行表示“强制更新”应用（即使在排除列表中也会强制更新）。
- 可以通过在路径后添加 `|admin` 来指定是否以管理员权限启动应用。
- 空行或仅包含空白字符的行会被忽略。
- 特殊规则：
  - 单独一行 `*` 表示“只更新强制对象，其他所有应用都跳过”，并且会在控制台显示所有被跳过应用的信息。

### 示例：

```
# 只更新强制对象，其他全部跳过
*
!AppID1=C:\Path\To\App1.exe|admin
!AppID2=C:\Path\To\App2.exe
AppID3
AppID4
!AppID3
```

- 上例中：
  - 只有 AppID1 和 AppID2 会被强制更新（并按配置启动指定应用），AppID3会被强制更新。AppID4 及其他所有应用都会被跳过，并在控制台显示跳过信息。
  - `!AppID3` 表示强制更新 AppID3 且不启动指定应用。
  - `|admin` 表示以管理员权限启动。

### 兼容性说明
- 如果未设置 `*`，则正常的排除/强制规则生效。
- 如果设置了 `*`，则仅处理强制对象，其他所有对象都会被跳过并显示通知。

## 代理服务器配置

如果需要通过代理服务器访问网络，可以创建 `proxy.txt` 文件来设置代理。

### proxy.txt 配置格式

```text
# 代理服务器配置文件
# 格式支持以下几种：
http://proxy.example.com:8080
https://proxy.example.com:8080
proxy.example.com:8080  # 自动添加 http://

# 示例：
http://127.0.0.1:8080
192.168.1.100:8080
```

### 代理配置说明

- 如果不需要代理，删除 `proxy.txt` 文件或注释掉所有行即可。
- 支持 HTTP 和 HTTPS 代理协议。
- 如果只提供 `host:port` 格式，会自动添加 `http://` 前缀。
- 代理配置会应用于所有 winget 网络请求。
- 配置更改后会在下次循环时自动重新加载。

## 检查间隔配置

可以通过 `check_interval.txt` 文件自定义更新检查的时间间隔。

### check_interval.txt 配置格式

```text
# 检查间隔配置文件
# 支持的格式:
# - 数字 + h/H: 小时
# - 数字 + m/M: 分钟  
# - 数字 + s/S: 秒
# - 纯数字: 秒

# 示例:
24h     # 24小时
12h     # 12小时
6h      # 6小时
30m     # 30分钟
3600s   # 3600秒
86400   # 86400秒（24小时）
```

### 检查间隔配置说明

- 如果文件不存在，默认使用24小时间隔。
- 支持小数，如 `1.5h`（1.5小时）或 `90m`（90分钟）。
- 配置更改后会在下次循环时自动重新加载。
- 建议最小间隔不少于30分钟，避免过于频繁的检查。

## 实时显示功能

**新功能：实时显示 winget 升级过程**

应用升级时现在支持实时显示 winget 的输出信息，让用户能够即时了解升级进度和状态。

### 实时显示特性

- ✅ **实时输出**: 升级过程中实时显示 winget 的所有输出信息
- ✅ **多语言支持**: 支持中文、英文、日文的实时输出标识
- ✅ **错误处理**: 智能处理编码问题和异常情况
- ✅ **保持兼容**: 保持原有功能的完整性，不影响现有逻辑
- ✅ **清晰格式**: 使用分隔线和缩进清晰地标识实时输出内容

### 实时显示示例

```
开始升级 Microsoft.VisualStudioCode，实时输出如下：
==================================================
  Found Microsoft Visual Studio Code [Microsoft.VisualStudioCode] Version 1.85.0
  This application is licensed to you by its owner.
  Downloading https://github.com/microsoft/vscode/releases/download/1.85.1/VSCodeSetup-x64-1.85.1.exe
  ██████████████████████████████  32.0 MB / 32.0 MB
  Successfully verified installer hash
  Starting package install...
  Successfully installed
==================================================
更新成功: Microsoft.VisualStudioCode [1.85.1]
```

### 技术实现

- 使用 `subprocess.Popen` 创建非阻塞进程
- 通过 `readline()` 实时读取输出流
- 自动处理 Windows 系统的 GBK 编码
- 智能错误处理和异常捕获

## 命令行参数与高级用法

- `--dry-run`：仅预览将要升级的应用，不执行实际升级和启动（适合测试和定时任务预览）。
- `--once`：只执行一次升级检查，不进入24小时循环（适合定时任务或手动触发）。

### 示例：

```bash
python AutoUpgradeApp.py --dry-run
python AutoUpgradeApp.py --once
python AutoUpgradeApp.py --dry-run --once
```

## 业务流程结构

- 主入口 `main()` 负责参数解析、权限检查和调度主循环。
- `monitor_updates()` 支持定时循环或单次执行。
- `check_and_update_apps()` 负责遍历所有可升级应用，按策略判断并调度升级。
- `process_upgrade_item()` 处理单个应用的升级/跳过/强制/排除等业务逻辑。
- `launch_app_by_id()` 支持升级后自动启动指定应用。

## 启动应用的输出行为

- 通过 `launch_app_by_id()` 启动的应用，其标准输出和错误输出均被重定向（不会显示在当前控制台窗口），以避免干扰主脚本日志和输出。
- 这一行为适用于所有自动升级后自动启动的应用，无论是否以管理员权限启动。
- 如需查看被启动应用的输出，请手动运行对应程序。

## 常见问题（FAQ）

**Q1: 为什么升级后自动启动的应用没有任何输出？**  
A: 所有通过 `launch_app_by_id()` 启动的应用，其标准输出和错误输出均被重定向（不会显示在当前控制台窗口），以避免干扰主脚本日志。如需查看输出，请手动运行对应程序。

**Q2: 如何只升级部分应用或排除某些应用？**  
A: 请编辑 `update_policy.txt`，按规则填写排除和强制更新对象。可用 `*` 规则只升级强制对象，其余全部跳过。

**Q3: 脚本为什么需要管理员权限？**  
A: winget 执行大部分应用升级操作需要管理员权限，否则会失败或部分升级无效。

**Q4: 日志文件在哪里？如何自定义？**  
A: 日志文件路径和格式可在 `output.py` 中调整，所有 info/warn/error 级别日志均会记录。

**Q5: 为什么英文/日文界面下部分提示不完整？**  
A: 由于系统限制，`lang.json` 中英文和日文的 `titles`、`all_latest` 等字段未完全测试，建议根据实际输出自行调整。

**Q6: 如何与 Windows 任务计划程序或 CI/CD 集成？**  
A: 推荐使用 `--once` 或 `--dry-run --once` 参数，结合计划任务定时触发，详见“命令行参数与高级用法”章节。

**Q7: 支持哪些 Windows 版本？**  
A: 仅支持 Windows 10/11，需预装 winget 1.3+ 和 Python 3.7+。

**Q8: 如何配置代理服务器？**  
A: 创建 `proxy.txt` 文件，填入代理服务器地址（如 `http://proxy.example.com:8080`）。不需要代理时删除该文件即可。配置会在下次循环时自动重新加载。

**Q9: 如何修改检查更新的时间间隔？**  
A: 创建或编辑 `check_interval.txt` 文件，设置期望的时间间隔。支持格式如 `24h`（24小时）、`30m`（30分钟）、`3600s`（3600秒）或 `86400`（纯数字秒）。

**Q10: 出现 "AttributeError: '_io.TextIOWrapper' object has no attribute 'mode'" 错误怎么办？**  
A: 这是早期版本中文本模式检测的问题，已在最新版本中修复。更新到最新版本即可解决。如仍有问题，请重新下载完整代码。

**Q11: 为什么还会显示"跳过用户指定更新: 但需要显式目标才能进行升级"这样的信息？**  
A: 这是winget的提示信息行，不是真正的应用更新项。最新版本已经改进了解析逻辑，会自动过滤这类异常格式的提示行，避免误报。

## 主要变更与最佳实践

- 支持 update_policy.txt 中 `*` 规则，仅强制对象更新，其余全部跳过。
- 多语言与配置加载分离，便于自定义和国际化。
- 工具函数与主流程分离，结构清晰，易于维护。
- 支持 dry-run 预览和单次执行，适合自动化运维和测试。
- 建议结合 Windows 任务计划程序定时触发 `--once` 或 `--dry-run --once`。

## 项目结构与模块职责

- `AutoUpgradeApp.py`：主入口，仅负责参数解析、权限检查和主循环调度。
- `upgrade.py`：升级、遍历、启动等核心业务逻辑。
- `config.py`：配置与多语言加载、策略文件解析。
- `utils.py`：通用工具函数（如字符串宽度、时间处理等）。
- `output.py`：统一输出与日志，支持 info/warn/error 多级别及日志文件。

## 类型注解与文档

- 全项目所有函数和主要变量均已补充类型注解，提升类型安全和可读性。
- 所有模块均补充详细文档字符串，便于 IDE/自动化工具集成和二次开发。

## 日志与输出机制

- 所有输出均通过 output.py 封装，支持 info/warn/error 多级别输出。
- 支持日志文件记录，便于问题追踪和自动化运维。
- 控制台输出与日志解耦，便于定制和集成。

## 异常处理与自动化集成

- 所有关键异常均详细输出堆栈信息，便于排查。
- 主流程和 upgrade.py 关键异常处均使用 sys.exit(1)/sys.exit(0) 友好退出，适合自动化集成。
- 建议结合 Windows 任务计划程序、CI/CD 等自动化工具，定期触发 `--once` 或 `--dry-run --once`。

---


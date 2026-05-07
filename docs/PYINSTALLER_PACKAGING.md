# PyInstaller 桌面打包说明

这个项目可以作为本地 Web 应用打成桌面包：可执行文件启动 FastAPI 服务，然后打开本机浏览器访问图鉴页。

## 1. 安装打包依赖

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
```

## 2. 先测试桌面入口

```bash
python3 run_desktop.py
```

默认会打开：

```text
http://127.0.0.1:8765/dex
```

如果 `8765` 被占用，入口会自动换一个空闲端口。

## 3. 打包

```bash
python3 scripts/build_desktop.py
```

产物会生成在：

```text
dist/洛克模拟器/
```

PyInstaller 生成的 `.spec` 文件会放在 `build/pyinstaller-spec/`，属于构建中间文件。

运行：

```bash
dist/洛克模拟器/洛克模拟器
```

## 4. 可选参数

隐藏控制台窗口：

```bash
python3 scripts/build_desktop.py --windowed
```

只查看 PyInstaller 命令，不执行打包：

```bash
python3 scripts/build_desktop.py --dry-run
```

指定应用名：

```bash
python3 scripts/build_desktop.py --name NRC-Roco
```

## 5. 注意

第一版建议用 `onedir`，不要急着做 `onefile`。本项目的 `data/` 和 `web/` 资源较大，`onedir` 更稳定，也更方便排查缺文件问题。

打包脚本默认排除了爬虫、表格处理、绘图、Jupyter 等开发期依赖；桌面端只保留运行 FastAPI、本地数据和静态页面所需的内容。

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

## 3. 打包原则

PyInstaller 通常不做跨平台打包。Windows 版本请在 Windows 上打包，macOS 版本请在 macOS 上打包。

项目的打包入口统一是：

```text
scripts/build_desktop.py
```

脚本会自动把 `web/` 和 `data/` 作为运行资源加入产物，并根据当前系统处理 PyInstaller 的资源路径分隔符。

## 4. Windows 打包

```bat
cd %USERPROFILE%\Desktop\Programming\Github_Project\roco-battle-simulator
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python scripts\build_desktop.py --windowed
```

产物默认生成在：

```text
dist\洛克模拟器\洛克模拟器.exe
```

如果希望先保留控制台窗口方便排查问题，可以去掉 `--windowed`：

```bat
python scripts\build_desktop.py
```

## 5. macOS 打包

```bash
python3 scripts/build_desktop.py
```

终端版产物会生成在：

```text
dist/洛克模拟器/
```

PyInstaller 生成的 `.spec` 文件会放在 `build/pyinstaller-spec/`，属于构建中间文件。

运行：

```bash
dist/洛克模拟器/洛克模拟器
```

如果希望生成 `.app`，使用：

```bash
python3 scripts/build_desktop.py --windowed
```

产物通常为：

```text
dist/洛克模拟器.app
```

可通过 Finder 双击，或在终端运行：

```bash
open dist/洛克模拟器.app
```

## 6. 可选参数

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

指定图标：

```bash
python3 scripts/build_desktop.py --icon path/to/app.ico
python3 scripts/build_desktop.py --icon path/to/app.icns
```

## 7. 重新打包

如果遇到旧资源没有更新，可以先删除构建产物再重新打包。

Windows：

```bat
rmdir /s /q build dist
python scripts\build_desktop.py --windowed
```

macOS：

```bash
rm -rf build dist
python3 scripts/build_desktop.py --windowed
```

## 8. GitHub Actions 自动打包

仓库内置工作流：

```text
.github/workflows/build-desktop.yml
```

触发方式：

- 在 GitHub 仓库页面进入 `Actions`，选择 `Build Desktop Apps`，点击 `Run workflow`。
- 推送 `v*` 标签，例如 `v0.1.0`，会自动打包。

工作流会在 GitHub 托管 runner 上分别构建：

- Windows：`windows-latest`，上传 `roco-battle-simulator-windows.zip`
- macOS：`macos-latest`，上传 `roco-battle-simulator-macos.zip`

发布新版本时可以用：

```bash
git tag v0.1.0
git push origin v0.1.0
```

打包完成后，在对应 workflow run 的 `Artifacts` 区域下载产物。

## 9. 注意

第一版建议用 `onedir`，不要急着做 `onefile`。本项目的 `data/` 和 `web/` 资源较大，`onedir` 更稳定，也更方便排查缺文件问题。

打包脚本默认排除了爬虫、表格处理、绘图、Jupyter 等开发期依赖；桌面端只保留运行 FastAPI、本地数据和静态页面所需的内容。

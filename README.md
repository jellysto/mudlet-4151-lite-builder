# Mudlet 4.15.1 Lite — GitHub Actions 自动编译 + NSIS 安装包

这套文件用于在 GitHub 仓库里自动编译一个裁剪版的 Mudlet 4.15.1（Windows 64 位），
并产出**带安装向导的 NSIS 安装包**和便携 zip。

## 裁剪掉的功能

| 功能 | 关闭方式 |
|------|----------|
| Updater | 环境变量 `WITH_UPDATER=NO` |
| 3D 地图 | 环境变量 `WITH_3DMAPPER=NO` |
| IRC | 移除菜单入口 + 槽函数置空（`apply_lite_patch.py`） |
| Discord Rich Presence | 移除菜单入口 + 槽函数置空（`apply_lite_patch.py`） |
| 语音 / TextToSpeech | `QT -= texttospeech`，且不安装该 Qt 模块 |
| 拼写检查 / Hunspell | 头文件桩（no-op）+ 去掉链接，安装包不含 hunspell DLL |

> IRC 与 Discord 的类本身与 `Host`/`mudlet.cpp` 深度耦合，直接删源码极易编译失败，
> 因此采用“移除菜单入口 + 槽函数置空”的方式：功能在界面上完全不可达，但代码仍参与
> 编译链接，保证构建可靠。如果你需要连二进制符号都彻底清除，需要针对具体版本做
> 更深入的源码手术（不在本方案范围内）。

保留的功能：内置字体、可变启动画面、Qt5Keychain（内置自有实现，不要设
`WITH_OWN_QTKEYCHAIN=NO`）、手柄 / Gamepad。这些均未在 workflow 中禁用
（`WITH_FONTS` / `WITH_VARIABLE_SPLASH_SCREEN` 不设为 `NO` 即默认启用）。

## 附带的 Bug 修复

| 问题 | 修复 |
|------|------|
| `resetProfile()` 每次重置都泄漏整个 Lua 堆（脚本、房间表、闭包、触发器） | 在 `TLuaInterpreter::initLuaGlobals()` 的 `pGlobalLua = luaL_newstate();` 前加入 `if (pGlobalLua) { lua_close(pGlobalLua); }`，与上游 4.21.0 的修法一致 |

触发场景：手动 reset、发呆被动重置、晕倒、死亡、断线重连都会走到该路径。
该修复已集成进 `apply_lite_patch.py`，若定位不到目标代码会直接报错中止构建。
安全性：4.15.1 的构造函数在首次调用 `initLuaGlobals()` 前已将 `pGlobalLua` 置为
`nullptr`，因此首次调用时 `if (pGlobalLua)` 为假，不会误关。

## 目录结构

```
mudlet-4.15.1-build/
├── .github/
│   └── workflows/
│       └── build-mudlet-4151.yml     # GitHub Actions 工作流
├── patches/
│   ├── apply_lite_patch.py           # 功能裁剪脚本
│   └── stubs/hunspell/               # Hunspell no-op 桩头文件
│       ├── hunspell.h
│       └── hunspell.hxx
├── installer/
│   └── mudlet-4.15.1-lite.nsi        # NSIS 安装向导脚本
└── README.md                         # 本文件
```

## 使用方法

### 1. 新建一个 GitHub 仓库

在 GitHub 上新建一个**公开或私有仓库**，例如 `mudlet-4151-lite-builder`。
把本目录（`mudlet-4.15.1-build`）里的所有内容（含隐藏的 `.github` 目录）提交到该仓库：

```bash
cd mudlet-4.15.1-build
git init
git add -A
git commit -m "Add Mudlet 4.15.1 lite build"
git remote add origin https://github.com/<你的用户名>/mudlet-4151-lite-builder.git
git push -u origin main
```

> 注意：`.github` 是隐藏目录，`git add -A` 会一并加入；如果用图形界面提交，请确认它被包含。

### 2. 触发编译

- 进入仓库的 **Actions** 页面；
- 左侧选择工作流 **Build Mudlet 4.15.1 Lite (NSIS Installer)**；
- 点击 **Run workflow**，选择 `main` 分支，再点绿色按钮。

也可以直接 `git push` 到 `main` 分支自动触发。

### 3. 下载产物

编译完成后（约 20–60 分钟，取决于缓存和机器），在本次运行的页面底部
**Artifacts** 区域下载 `Mudlet-4.15.1-Lite-Windows`，里面包含：

- `Mudlet-4.15.1-Lite-Setup.exe` —— NSIS 安装向导
- `mudlet-4.15.1-lite-portable.zip` —— 免安装便携版

> GitHub 免费账户的 artifact 默认保留 90 天；私有仓库的 artifact 也可以下载。
> 如果 Actions 报 “Resource not accessible by integration”，请把仓库设为公开，
> 或在 Settings → Actions → General → Workflow permissions 里勾选 “Read and write permissions”。

## 编译环境（工作流已配置，无需手动干预）

旧方案依赖 Mudlet 官方 `appveyor.install.ps1`，它从十几个 2015 年前后的老下载站
（osdn.net、sourceforge、overbyte.eu 等）拉取并源码编译依赖，目前这些源大量失效。
因此本方案改为**全程 MSYS2**，所有依赖从 MSYS2 的软件仓库安装，稳定可靠：

- Runner：`windows-2022`
- 环境：MSYS2 **UCRT64**（必须用这个环境，因为只有 UCRT64/CLANG64 还提供 Lua 5.1）
- Qt：`5.15.x`（MSYS2 包 `mingw-w64-ucrt-x86_64-qt5-*`，满足 4.15.1 要求的 Qt ≥ 5.11）
- 依赖：`pacman` 安装 lua51 / pcre / zlib / libzip / pugixml / boost / yajl / sqlite /
  openssl / luarocks 及常用 Lua 5.1 模块
- 构建：`WITH_MAIN_BUILD_SYSTEM=NO`（选用 mudlet.pro 的 MSYS2 分支）+ `WITH_UPDATER=NO`
  + `WITH_3DMAPPER=NO`，然后 `qmake` + `mingw32-make`
- 部署：MSYS2 的 `windeployqt` + 从 `/ucrt64/bin` 复制非 Qt DLL
- 打包：NSIS（`choco install nsis`）

## 已知注意事项

1. **首次运行可能需微调**：MSYS2 的包版本会更新，若某次编译因库名/头文件路径变化失败，
   请按 Actions 日志里的报错调整 workflow 的包名或 `apply_lite_patch.py` 的库名适配。
   常见的两个已处理的适配点：PCRE 链接名 `-lpcre-1` → `-lpcre`；Hunspell 用桩头文件。
2. **裁剪脚本对 tag 敏感**：`apply_lite_patch.py` 用正则匹配 `Mudlet-4.15.1` 的源码。
   若更换 tag，脚本会打印 `[WARN] ... no match` 提示哪些替换未命中，请据此调整脚本。
   Lua 泄漏修复是强制项，定位不到会直接报错中止构建。
3. **Hunspell 桩的兼容性**：桩头文件 `patches/stubs/hunspell/` 实现了 Mudlet 4.15.1
   用到的 C/C++ Hunspell API。如果编译时报某个 `Hunspell_*` 或 `Hunspell::` 方法未定义，
   说明还有遗漏的 API，按报错把对应 no-op 函数补进 `hunspell.h` / `hunspell.hxx` 即可。
4. **GPL 合规**：Mudlet 是 GPL 项目。发布这个自定义构建时，请随安装包附上
   `LICENSE` 和对应源码（可以将本构建仓库设为公开，并在 About 里注明是基于
   Mudlet 4.15.1 修改的构建）。

## 本地等价构建（可选）

如果你想在本地 Windows 上复现，不依赖 GitHub Actions，可以按下面顺序手工执行：

1. 安装 MSYS2，打开 **UCRT64** 终端；
2. 按 workflow 里的 `pacman -S` 清单安装依赖；
3. Clone Mudlet 并切到 tag：`git clone -b Mudlet-4.15.1 https://github.com/Mudlet/Mudlet.git`；
4. 运行 `python patches/apply_lite_patch.py <Mudlet目录>`；
5. `cd Mudlet/src`，设置 `MINGW_BASE_DIR=/ucrt64`、`WITH_MAIN_BUILD_SYSTEM=NO`、
   `WITH_UPDATER=NO`、`WITH_3DMAPPER=NO`
   （不要设置 `WITH_FONTS` 和 `WITH_VARIABLE_SPLASH_SCREEN`，保留内置字体与启动画面），再执行：
   ```bash
   qmake CONFIG+=release mudlet.pro
   mingw32-make -j8
   ```
6. `cd release`，执行 `windeployqt mudlet.exe`，按工作流里的清单复制 DLL 和数据文件；
7. 用 `makensis /DMUDLET_VERSION=4.15.1 /DRELEASE_DIR=<release目录> installer\mudlet-4.15.1-lite.nsi` 打包。

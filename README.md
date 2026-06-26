# BROAD AIR for Home Assistant

[English README](README.en.md)

这是一个面向 BROAD / 远大新风系统的 Home Assistant 自定义集成。

它通过远大官方 BROAD AIR 云 API 登录账号、发现账号下的新风设备、暴露常用传感器，并提供基础的新风机开关和目标频率控制。

当前主要基于真实 BROAD AIR 账号和一台 `SQ260` 新风机开发验证。其他型号可以安装使用，但能力范围还需要社区或实机继续确认。

## 功能

- Home Assistant UI 配置流程。
- 使用官方 App 同款签名方式登录 BROAD AIR 云 API。
- 当云端让旧 token 失效时自动重新登录并重试一次。
- 自动发现账号下的新风设备。
- 周期轮询状态，并在控制命令后通过实时刷新接口更新状态。
- 暴露温度、CO2、PM2.5、风量、功率、运行状态、故障状态等常用实体。
- 电源开关实体。
- 目标频率 number 实体。
- 按设备解析频率范围：
  - 手动 options 覆盖
  - API 状态字段
  - 已知型号表，例如 `SQ260`
  - 安全兜底范围
- diagnostics 诊断信息会脱敏敏感字段。
- 支持作为 HACS custom repository 安装。
- 集成图标和 logo 位于 `custom_components/broadair/brand/`。

## 安装

### 通过 HACS custom repository 安装

这个仓库还没有进入 HACS 默认商店，需要先作为 custom repository 添加：

1. 打开 Home Assistant。
2. 打开 **HACS**。
3. 进入 **Integrations**。
4. 点击右上角菜单。
5. 选择 **Custom repositories**。
6. 添加仓库地址：

   ```text
   https://github.com/Team-Cyan/broadair-hass-integration
   ```

7. Category 选择 **Integration**。
8. 点击 **Add**。
9. 在 HACS 里搜索并安装 **BROAD AIR**。
10. 重启 Home Assistant。
11. 进入 **设置 -> 设备与服务 -> 添加集成**。
12. 搜索 **BROAD AIR**，按配置流程添加账号。

### 手动安装

1. 下载或 clone 这个仓库。
2. 复制目录：

   ```text
   custom_components/broadair
   ```

3. 放到你的 Home Assistant 配置目录：

   ```text
   <home-assistant-config>/custom_components/broadair
   ```

4. 重启 Home Assistant。
5. 进入 **设置 -> 设备与服务 -> 添加集成**。
6. 搜索 **BROAD AIR**，按配置流程添加账号。

如果你使用 Docker 版 Home Assistant，配置目录通常在容器内挂载为 `/config`。

## 配置项

配置流程会要求填写这些字段：

| 字段 | 推荐值 |
| --- | --- |
| Username or phone number | 远大 BROAD AIR 账号手机号或用户名 |
| Password | BROAD AIR 账号密码 |
| API base URL | 保持默认 `https://broadcleanair.net:8103` |
| Verify SSL certificate | 默认 API host 建议关闭 |
| Scan interval | 默认 `60` 秒 |
| Minimum frequency override | 保持 `0`，表示自动检测 |
| Maximum frequency override | 保持 `0`，表示自动检测 |

官方 Android App 当前使用 `https://broadcleanair.net:8103`。这个地址返回的 TLS 证书和 hostname 不匹配，所以集成为了兼容官方 API，默认关闭 SSL 证书校验。

远大登录接口对时间戳比较敏感。集成会尽量使用 BROAD AIR 服务器时间生成登录签名，避免 Home Assistant 主机时间轻微漂移导致误报认证失败。

## 实体

实体名称会根据云端返回的设备名生成。

默认启用：

- 室内温度
- 室外温度
- 新风温度
- 排风温度
- CO2
- 室外 PM2.5
- 实时风量
- 当前运行频率
- 实时功率
- 在线状态
- 运行状态
- 故障状态
- 电源开关
- 目标频率

默认不启用，但可以在 Home Assistant 实体设置里手动启用：

- 第二室内温度
- 送风温度
- 室内湿度
- 送风湿度
- 室内 PM2.5
- 设定频率传感器
- 实时热回收

这些默认隐藏的实体在已验证的 `SQ260` 上更像型号相关字段、诊断字段、控制实体的重复信息，或占位值。

## 服务

集成注册了这些 service：

- `broadair.turn_on`
- `broadair.turn_off`
- `broadair.set_frequency`
- `broadair.refresh_realtime`

如果账号里只有一台新风机，可以不填 `device_guid`。

示例：

```yaml
service: broadair.set_frequency
data:
  frequency: 20
```

控制命令会串行执行，所以快速拖动 UI 不会因为 cooldown 直接报错。每次控制后，集成会优先把实时刷新接口返回的状态直接写入 Home Assistant 缓存，并安排一次延迟实时刷新，减少普通状态接口缓存导致的状态滞后。

## 频率范围

目标频率范围按每台设备解析：

1. 如果 options 里手动设置了 min/max，优先使用。
2. 如果云端状态字段提供有效范围，使用 API 字段。
3. 使用已知型号表，目前 `SQ260` 和 `SQ260-C1` 是 `20-50 Hz`。
4. 未知型号兜底为 `0-100 Hz`。

如果你的型号安全范围不同，可以在集成 options 里设置 **Minimum frequency override** 和 **Maximum frequency override**。

## 常见问题

### invalid_auth

先检查账号密码。如果账号密码正确，再检查 Home Assistant 主机时间是否准确。BROAD AIR 登录签名对时间比较敏感。

### token 被强制下线

官方 App 和 Home Assistant 使用同一个账号时，可能互相让对方的 session token 失效。集成会检测这种情况，并自动重新登录一次后重试请求。

### 图标不显示

图标和 logo 位于：

```text
custom_components/broadair/brand/
```

安装或更新后请重启 Home Assistant，并在浏览器里硬刷新页面，或完全重启 Home Assistant 手机 App 来清理前端缓存。

### SSL 报错

使用默认 API host 时，请保持 **Verify SSL certificate** 关闭。只有在你使用证书匹配的 API endpoint 时，才建议打开。

## 开发

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest
ruff check .
python3 -m compileall -q custom_components tests
```

## 发布检查

1. 更新 `custom_components/broadair/manifest.json`。
2. 更新 `pyproject.toml`。
3. 更新 `CHANGELOG.md`。
4. 运行 `ruff`、`pytest` 和 `compileall`。
5. 打 tag，例如 `vX.Y.Z`。
6. 发布 GitHub release。

## 文档

- [Roadmap](docs/roadmap.md)
- [Design](docs/design.md)
- [API notes](docs/api-notes.md)
- [Changelog](CHANGELOG.md)

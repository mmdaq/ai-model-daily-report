# AI 模型日报

每天自动采集 HuggingFace、GitHub、Civitai、魔搭 最新 AI 模型，按类别生成 HTML 日报，发布到 GitHub Pages，并可选发送 QQ 邮箱。

## 在线查看

启用 GitHub Pages 后，日报地址：

```
https://<你的用户名>.github.io/<仓库名>/
```

## GitHub Actions 部署（推荐，电脑不用常开）

### 1. 创建 GitHub 仓库

在 GitHub 新建仓库（如 `ai-model-daily-report`），将本目录 `ai_model_monitor` 推送上去。

```bash
cd ai_model_monitor
git init
git add .
git commit -m "init: AI model daily report"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

### 2. 配置 Secrets

仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret 名称 | 说明 |
|-------------|------|
| `QQ_EMAIL` | 发送邮箱，如 `385096659@qq.com` |
| `QQ_SMTP_AUTH_CODE` | QQ 邮箱 SMTP 授权码 |
| `RECEIVER_EMAIL` | 接收邮箱（可与发送邮箱相同） |

### 3. 开启 GitHub Pages

仓库 → **Settings** → **Pages**

- Source: **Deploy from a branch**
- Branch: **main** / **docs**

保存后几分钟内可访问在线日报。

### 4. 手动触发测试

仓库 → **Actions** → **AI Model Daily Report** → **Run workflow**

### 定时规则

- 每天 **北京时间 8:00** 自动运行（UTC 0:00）
- 自动采集 → 生成 HTML → 推送到 `docs/` → 可选发邮件

## 本地运行（可选）

```bash
pip install -r requirements.txt
copy .env.example .env   # 填写邮箱
python main.py --once    # 本地发邮件
python main.py --ci      # 本地测试 GitHub 发布模式
```

## 五大类别

- 文本大模型
- 文生图模型
- 图生图模型
- 文生视频模型
- 图生视频模型

每个模型以卡片形式展示：平台、标签、智脑小结、显存推荐、运行命令、仓库链接。

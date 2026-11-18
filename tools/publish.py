# -*- coding: utf-8 -*-
"""一键发布：重新生成网页 → 同步到在线版 → 提交 → 推送。

用法：
    python tools/publish.py "这次改了什么"
    python tools/publish.py "改了什么" --no-push     # 只提交不推送
    python tools/publish.py "改了什么" --no-commit   # 只生成文件，不动 git

做的事：
    1. 跑 build_web.py，把 data/ 重新打包成 dist/潜水艇材料计算器.html
    2. 复制到 docs/index.html（GitHub Pages 用的就是这个）
    3. git add -A + commit + push
"""
import os
import shutil
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "dist", "潜水艇材料计算器.html")
DOCS = os.path.join(ROOT, "docs", "index.html")


def run(cmd, cwd=ROOT, check=True):
    print("+ " + " ".join(cmd), flush=True)
    # 直接继承父进程的输出，避免 Windows 控制台编码问题
    code = subprocess.call(cmd, cwd=cwd)
    if check and code != 0:
        raise SystemExit("命令失败：%s" % " ".join(cmd))
    return code


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    message = args[0] if args else "更新页面 " + time.strftime("%Y-%m-%d %H:%M")

    # 1. 重新生成
    run([sys.executable, os.path.join(ROOT, "tools", "build_web.py")])
    if not os.path.exists(HTML):
        raise SystemExit("没有生成 html，检查 build_web.py")

    # 2. 同步到在线版
    os.makedirs(os.path.dirname(DOCS), exist_ok=True)
    shutil.copyfile(HTML, DOCS)
    print("已同步到 docs/index.html（%.1f KB）" % (os.path.getsize(DOCS) / 1024.0))

    if "--no-commit" in flags:
        print("跳过提交（--no-commit）")
        return 0

    # 3. 提交
    run(["git", "add", "-A"])
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8")
    if not status.stdout.strip():
        print("没有变化，跳过提交")
        return 0
    run(["git", "commit", "-m", message])

    # 4. 推送
    if "--no-push" in flags:
        print("跳过推送（--no-push），需要时手动跑 git push")
        return 0
    run(["git", "push"])
    print("完成。在线版 1~2 分钟后生效。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

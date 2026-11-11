"""Curated, copy-only Git reference used by the settings page."""


def entry(title, code, note=""):
    return {"title": title, "code": code, "note": note}


COMMAND_GROUPS = [
    {
        "id": "local",
        "title": "本地仓库与工作区",
        "icon": "repo",
        "commands": [
            entry("初始化本地仓库", "git init -b main"),
            entry(
                "克隆远程仓库到指定目录",
                "git clone https://github.com/OWNER/REPO.git my-project",
            ),
            entry("查看仓库根目录", "git rev-parse --show-toplevel"),
            entry("查看本地 Git 数据目录", "git rev-parse --git-dir"),
            entry("查看工作区与分支状态", "git status -sb"),
            entry("查看已跟踪文件", "git ls-files"),
            entry("查看未暂存的修改", "git diff"),
            entry("查看已暂存的修改", "git diff --staged"),
            entry("查看修改规模", "git diff --stat"),
        ],
    },
    {
        "id": "commit",
        "title": "暂存与提交",
        "icon": "commit",
        "commands": [
            entry("暂存指定文件", "git add path/to/file"),
            entry("分块选择要提交的修改", "git add -p"),
            entry("暂存所有新增、修改和删除", "git add -A"),
            entry(
                "取消指定文件的暂存",
                "git restore --staged path/to/file",
                "保留工作区中的修改。",
            ),
            entry("创建提交", 'git commit -m "Describe the change"'),
            entry(
                "修改最近一次提交说明",
                'git commit --amend -m "New commit message"',
                "会改写最近一次提交，优先用于尚未推送的提交。",
            ),
            entry(
                "将已暂存的修改补入最近一次提交",
                "git commit --amend --no-edit",
                "会生成新的提交 ID。",
            ),
        ],
    },
    {
        "id": "remote",
        "title": "远程地址与远程仓库",
        "icon": "remote",
        "commands": [
            entry("查看所有远程的拉取与推送地址", "git remote -v"),
            entry("查看 origin 的拉取地址", "git remote get-url origin"),
            entry(
                "查看 origin 的全部推送地址", "git remote get-url --push --all origin"
            ),
            entry(
                "为本地仓库添加 origin",
                "git remote add origin git@github.com:OWNER/REPO.git",
                "适用于尚未配置 origin 的仓库。",
            ),
            entry(
                "将已有 origin 切换为 SSH 地址",
                "git remote set-url origin git@github.com:OWNER/REPO.git",
            ),
            entry(
                "将已有 origin 切换为 HTTPS 地址",
                "git remote set-url origin https://github.com/OWNER/REPO.git",
            ),
            entry(
                "单独设置推送地址",
                "git remote set-url --push origin git@github.com:OWNER/REPO.git",
                "只修改 push URL，fetch URL 不变。",
            ),
            entry(
                "为 Fork 添加上游仓库",
                "git remote add upstream https://github.com/UPSTREAM/REPO.git",
            ),
            entry(
                "查看远程分支与跟踪关系",
                "git remote show origin",
                "此命令会查询远程仓库。",
            ),
            entry("重命名远程配置", "git remote rename origin old-origin"),
            entry(
                "移除远程配置",
                "git remote remove upstream",
                "移除本地的远程配置与对应远程跟踪引用，不会删除服务器上的仓库。",
            ),
        ],
    },
    {
        "id": "branch",
        "title": "本地分支与远程分支",
        "icon": "branch",
        "commands": [
            entry("查看本地分支及跟踪关系", "git branch -vv"),
            entry("查看远程跟踪分支", "git branch -r"),
            entry("查看全部分支", "git branch -a"),
            entry("创建并切换到功能分支", "git switch -c feature/login"),
            entry("切换到已有分支", "git switch main"),
            entry(
                "从远程分支创建本地跟踪分支", "git switch --track origin/feature/login"
            ),
            entry("重命名本地分支", "git branch -m old-name new-name"),
            entry(
                "删除已合并的本地分支",
                "git branch -d feature/login",
                "请先切换到其他分支；Git 会检查该分支是否已合并。",
            ),
            entry(
                "删除远程分支",
                "git push origin --delete feature/login",
                "会删除服务器上的指定分支。",
            ),
        ],
    },
    {
        "id": "sync",
        "title": "拉取、推送与上游同步",
        "icon": "sync",
        "commands": [
            entry(
                "获取 origin 更新并清理已失效的远程跟踪引用", "git fetch --prune origin"
            ),
            entry("获取所有远程的更新", "git fetch --all --prune"),
            entry(
                "仅允许快进方式拉取",
                "git pull --ff-only",
                "分支发生分叉时会停止，需自行选择合并或变基。",
            ),
            entry("首次推送并建立跟踪关系", "git push -u origin feature/login"),
            entry("推送当前分支到已配置的上游", "git push"),
            entry(
                "将本地分支推送为另一远程分支名",
                "git push origin local-branch:remote-branch",
            ),
            entry(
                "设置已有分支的上游", "git branch --set-upstream-to=origin/main main"
            ),
            entry("查看本地尚未推送的提交", "git log --oneline origin/main..main"),
            entry(
                "查看远程新增、本地没有的提交",
                "git log --oneline main..origin/main",
                "先执行 git fetch 更新远程跟踪引用。",
            ),
            entry(
                "同步 Fork 的主分支",
                "git fetch upstream\ngit switch main\ngit merge --ff-only upstream/main\ngit push origin main",
                "要求 upstream 已配置；若主分支分叉，快进合并会停止。",
            ),
        ],
    },
    {
        "id": "merge",
        "title": "合并分支与解决冲突",
        "icon": "merge",
        "commands": [
            entry(
                "将功能分支合并到 main",
                "git switch main\ngit merge feature/login",
                "合并目标是当前分支；开始前先提交或暂存工作区修改。",
            ),
            entry(
                "保留独立合并提交", "git switch main\ngit merge --no-ff feature/login"
            ),
            entry(
                "压缩功能分支为一次提交",
                'git merge --squash feature/login\ngit commit -m "Merge login feature"',
                "在目标分支执行；产生普通提交，不记录 merge 父节点。",
            ),
            entry("查看尚未解决冲突的文件", "git diff --name-only --diff-filter=U"),
            entry(
                "标记冲突已解决并继续合并",
                "git add path/to/resolved-file\ngit merge --continue",
                "先编辑冲突文件并处理冲突标记；解决全部冲突后继续。",
            ),
            entry(
                "取消当前合并",
                "git merge --abort",
                "用于正在进行的合并；合并前的未提交修改可能无法完整恢复。",
            ),
        ],
    },
    {
        "id": "rebase",
        "title": "变基与挑选提交",
        "icon": "branch",
        "commands": [
            entry(
                "将当前功能分支变基到最新 main",
                "git fetch origin\ngit rebase origin/main",
                "改写当前分支的提交历史，适合尚未共享的功能分支。",
            ),
            entry(
                "解决冲突后继续变基",
                "git add path/to/resolved-file\ngit rebase --continue",
            ),
            entry("取消当前变基", "git rebase --abort"),
            entry(
                "整理最近三个提交",
                "git rebase -i HEAD~3",
                "交互式调整顺序、合并提交或修改说明；会改写历史。",
            ),
            entry("将指定提交应用到当前分支", "git cherry-pick COMMIT_SHA"),
            entry(
                "冲突解决后继续挑选提交",
                "git add path/to/resolved-file\ngit cherry-pick --continue",
            ),
            entry("取消当前挑选提交", "git cherry-pick --abort"),
            entry(
                "变基后更新远程功能分支",
                "git push --force-with-lease origin feature/login",
                "会改写远程历史；与协作者确认后使用。远程引用与本地预期不一致时会拒绝推送。",
            ),
        ],
    },
    {
        "id": "stash",
        "title": "临时保存工作",
        "icon": "archive",
        "commands": [
            entry(
                "保存修改与未跟踪文件",
                'git stash push -u -m "work in progress"',
                "-u 包含未跟踪文件，不包含被忽略的文件。",
            ),
            entry("查看暂存记录", "git stash list"),
            entry("查看最近一条暂存内容", "git stash show -p 'stash@{0}'"),
            entry("恢复记录并保留暂存记录", "git stash apply 'stash@{0}'"),
            entry(
                "恢复记录并在成功后移除记录",
                "git stash pop 'stash@{0}'",
                "发生冲突时，暂存记录会保留。",
            ),
            entry("从暂存记录创建分支", "git stash branch recover-work 'stash@{0}'"),
            entry(
                "删除指定暂存记录",
                "git stash drop 'stash@{0}'",
                "确认不再需要这条记录后执行。",
            ),
        ],
    },
    {
        "id": "history",
        "title": "日志、比较与定位",
        "icon": "history",
        "commands": [
            entry("查看分支提交图", "git log --oneline --graph --decorate --all"),
            entry("查看最近一次提交的内容", "git show HEAD"),
            entry("比较两个分支当前文件状态", "git diff main feature/login"),
            entry("查看功能分支相对共同祖先的修改", "git diff main...feature/login"),
            entry("查看某个文件的历史", "git log --follow -- path/to/file"),
            entry("查看每行代码来自哪个提交", "git blame path/to/file"),
            entry("按提交说明搜索", 'git log --all --oneline --grep="keyword"'),
            entry("按内容变化搜索提交", 'git log -S "function_name" -- path/to/file'),
            entry("在已跟踪文件中搜索", 'git grep -n "keyword"'),
        ],
    },
    {
        "id": "undo",
        "title": "撤销、回退与恢复",
        "icon": "undo",
        "commands": [
            entry(
                "撤销指定文件未暂存的修改",
                "git restore path/to/file",
                "会丢弃该文件未暂存的修改。",
            ),
            entry(
                "撤销最近一次提交，修改保留在暂存区",
                "git reset --soft HEAD~1",
                "改写本地分支历史，适用于尚未推送的提交。",
            ),
            entry(
                "撤销最近一次提交并取消暂存",
                "git reset --mixed HEAD~1",
                "保留工作区修改，但会改写本地分支历史。",
            ),
            entry(
                "用新提交撤销已有提交",
                "git revert COMMIT_SHA",
                "保留原有历史，适合已经共享的提交。",
            ),
            entry("查看本地引用变更记录", "git reflog"),
            entry(
                "从历史提交恢复为新分支",
                "git switch -c recovered COMMIT_SHA",
                "先从 reflog 找到要恢复的提交 ID。",
            ),
            entry("预览未跟踪文件的清理范围", "git clean -nd", "只预览，不删除。"),
            entry(
                "清理未跟踪文件与目录",
                "git clean -fd",
                "会删除未跟踪文件与目录；先检查 git clean -nd 的结果。",
            ),
            entry(
                "强制将本地分支与 origin/main 对齐",
                "git fetch origin\ngit reset --hard origin/main",
                "会丢弃当前分支的本地提交及已跟踪文件的未提交修改；执行前先备份需要保留的内容。",
            ),
        ],
    },
    {
        "id": "tags",
        "title": "标签与发布",
        "icon": "tag",
        "commands": [
            entry("查看标签", "git tag --list"),
            entry("创建带说明的标签", 'git tag -a v1.0.0 -m "Release v1.0.0"'),
            entry("查看标签对应内容", "git show v1.0.0"),
            entry("推送指定标签", "git push origin v1.0.0"),
            entry("删除本地标签", "git tag -d v1.0.0"),
            entry(
                "删除远程标签",
                "git push origin --delete refs/tags/v1.0.0",
                "会删除服务器上的指定标签。",
            ),
            entry(
                "导出当前提交为 ZIP",
                "git archive --format=zip --output=project.zip HEAD",
                "只包含当前提交中跟踪的文件，不包含 .git 目录。",
            ),
        ],
    },
    {
        "id": "config",
        "title": "配置、忽略与多个工作目录",
        "icon": "settings",
        "commands": [
            entry("查看生效配置及来源", "git config --list --show-origin"),
            entry("查看当前仓库配置", "git config --local --list"),
            entry(
                "设置当前仓库提交身份",
                'git config --local user.name "Your Name"\ngit config --local user.email "you@example.com"',
            ),
            entry(
                "设置全局默认身份",
                'git config --global user.name "Your Name"\ngit config --global user.email "you@example.com"',
                "对未覆盖身份设置的仓库生效；多账号可使用下方的按目录配置。",
            ),
            entry("检查文件被哪条规则忽略", "git check-ignore -v path/to/file"),
            entry(
                "停止跟踪文件，但保留本地文件",
                "git rm --cached path/to/file",
                "再将路径加入 .gitignore，并提交变更。",
            ),
            entry("查看所有 worktree", "git worktree list"),
            entry(
                "在另一个目录创建独立分支工作区",
                "git worktree add -b feature/new ../repo-feature main",
            ),
            entry(
                "移除已完成的 worktree",
                "git worktree remove ../repo-feature",
                "会删除该工作目录；有未提交修改时默认拒绝。",
            ),
            entry("初始化仓库的子模块", "git submodule update --init --recursive"),
        ],
    },
]

ACCOUNT_STEPS = [
    {
        "title": "为个人与工作账号生成独立密钥",
        "description": "在终端执行。示例邮箱、用户名和仓库名需替换为你的实际信息；若相同文件已存在，请使用新的文件名。以下路径适用于 macOS、Linux 或 Git Bash。",
        "blocks": [
            entry(
                "生成两组密钥",
                'ssh-keygen -t ed25519 -C "personal@example.com" -f ~/.ssh/id_ed25519_personal\nssh-keygen -t ed25519 -C "work@example.com" -f ~/.ssh/id_ed25519_work',
            ),
            entry(
                "加载到 SSH Agent",
                'eval "$(ssh-agent -s)"\nssh-add ~/.ssh/id_ed25519_personal\nssh-add ~/.ssh/id_ed25519_work',
            ),
        ],
    },
    {
        "title": "将公钥分别添加到对应平台账号",
        "description": "分别登录个人与工作 GitHub 账号，在 Settings → SSH and GPG keys 中添加对应的 .pub 文件内容。Gitee 使用个人设置中的 SSH 公钥入口。",
        "blocks": [
            entry("读取个人公钥", "cat ~/.ssh/id_ed25519_personal.pub"),
            entry("读取工作公钥", "cat ~/.ssh/id_ed25519_work.pub"),
        ],
    },
    {
        "title": "在 SSH 配置中定义账号别名",
        "description": "将以下配置合并到 ~/.ssh/config。IdentityFile 指向私钥文件；IdentitiesOnly 让每个别名使用指定的密钥。Gitee 的 HostName 可改为 gitee.com，并起一个独立别名。",
        "blocks": [
            entry(
                "~/.ssh/config",
                "Host github-personal\n    HostName github.com\n    User git\n    IdentityFile ~/.ssh/id_ed25519_personal\n    IdentitiesOnly yes\n\nHost github-work\n    HostName github.com\n    User git\n    IdentityFile ~/.ssh/id_ed25519_work\n    IdentitiesOnly yes",
            ),
            entry("设置配置文件权限（macOS / Linux）", "chmod 600 ~/.ssh/config"),
            entry(
                "验证认证账号",
                "ssh -T git@github-personal\nssh -T git@github-work",
                "确认欢迎信息中的用户名分别对应两个账号。GitHub 成功认证后也可能返回退出码 1，以欢迎信息为准。",
            ),
        ],
    },
    {
        "title": "让仓库使用对应的远程地址",
        "description": "SSH 的 Host 别名决定推送、拉取使用哪个账号。已有仓库使用 set-url；新仓库在 clone 时使用别名。",
        "blocks": [
            entry(
                "克隆个人或工作仓库",
                "git clone git@github-personal:PERSONAL_USER/REPO.git\ngit clone git@github-work:WORK_ORG/WORK_REPO.git",
            ),
            entry(
                "已有个人仓库切换账号",
                "git remote set-url origin git@github-personal:PERSONAL_USER/REPO.git",
            ),
            entry(
                "已有工作仓库切换账号",
                "git remote set-url origin git@github-work:WORK_ORG/REPO.git",
            ),
            entry(
                "核对拉取与推送地址",
                "git remote -v\ngit remote get-url --push --all origin",
                "如果以前单独配置过 push URL，还需用 git remote set-url --push origin 新地址 更新。",
            ),
        ],
    },
    {
        "title": "为本地仓库设置提交身份",
        "description": "在对应仓库目录下执行。user.name 和 user.email 记录提交作者，SSH Key 决定远程认证，两者需要分别配置。",
        "blocks": [
            entry(
                "当前个人仓库",
                'git config --local user.name "Personal Name"\ngit config --local user.email "personal@example.com"',
            ),
            entry(
                "当前工作仓库",
                'git config --local user.name "Work Name"\ngit config --local user.email "work@example.com"',
            ),
            entry(
                "检查实际生效的身份与来源",
                "git config --show-origin --get user.name\ngit config --show-origin --get user.email\ngit var GIT_AUTHOR_IDENT",
            ),
        ],
    },
    {
        "title": "按目录自动切换提交身份",
        "description": "将个人仓库放到 ~/projects/personal/，工作仓库放到 ~/projects/work/。把以下 includeIf 合并到 ~/.gitconfig，并创建两个独立配置文件。目录末尾的 / 会匹配其下仓库。",
        "blocks": [
            entry(
                "~/.gitconfig",
                '[user]\n    useConfigOnly = true\n\n[includeIf "gitdir:~/projects/personal/"]\n    path = ~/.gitconfig-personal\n\n[includeIf "gitdir:~/projects/work/"]\n    path = ~/.gitconfig-work',
            ),
            entry(
                "~/.gitconfig-personal",
                "[user]\n    name = Personal Name\n    email = personal@example.com",
            ),
            entry(
                "~/.gitconfig-work",
                "[user]\n    name = Work Name\n    email = work@example.com",
            ),
            entry(
                "在目标仓库内验证",
                "git config --show-origin --get user.email",
                "现有仓库的 --local 身份会覆盖 includeIf。确认切换到按目录管理后，可在该仓库执行 git config --local --unset-all user.name 和 user.email。若仍保留全局默认身份，未匹配目录仍可能使用全局值。",
            ),
        ],
    },
    {
        "title": "使用 HTTPS 时区分账号凭据",
        "description": "HTTPS 不使用 SSH Host 别名。通过系统凭据管理器保存各账号凭据；在 GitHub 输入认证凭据时使用 Token，提交作者仍按前面的步骤配置。",
        "blocks": [
            entry(
                "查看当前凭据助手",
                "git config --show-origin --get-all credential.helper",
            ),
            entry(
                "让 GitHub HTTPS 凭据包含仓库路径",
                "git config --global credential.https://github.com.useHttpPath true",
                "帮助按仓库路径区分凭据；旧凭据仍可能需要在系统凭据管理器中更新。",
            ),
            entry(
                "使用 HTTPS 远程地址",
                "git remote set-url origin https://github.com/OWNER/REPO.git",
            ),
        ],
    },
    {
        "title": "排查账号、权限与提交记录",
        "description": "依次检查 SSH 别名是否生效、远程地址使用的别名，以及本地提交身份。变更 user.email 不会修改已经存在的提交。",
        "blocks": [
            entry("检查 SSH 实际配置", "ssh -G github-work"),
            entry("查看 SSH 认证过程", "ssh -vT git@github-work"),
            entry(
                "检查远程地址与最近提交作者",
                "git remote -v\ngit config --show-origin --get user.email\ngit log -1 --format='%an <%ae>'",
            ),
        ],
    },
]

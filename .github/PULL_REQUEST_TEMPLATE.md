---
name: "🚀 发布新预制件版本"
title: "feat(publish): <prefab-id>@<version>"
---

## 预制件信息

- **预制件 ID:** `[your-prefab-id]`
- **版本号:** `[your-version]`
- **作者:** `[your-github-username]`
- **源码仓库:** `[repo-url]`

## 提交清单

在提交 Pull Request 之前，请确认以下事项：

- [ ] 我已经在源码仓库中创建了对应版本的 Release 并上传了 `.whl` 构件文件
- [ ] `id` 和 `version` 与上述信息一致
- [ ] `artifact_url` 指向一个公开可访问的 `.whl` 文件
- [ ] 我的 `prefab-manifest.json` 是有效的，且与 `community-prefabs.json` 中的信息一致
- [ ] 我已阅读并同意[贡献者许可协议](CONTRIBUTING.md)
- [ ] 我的代码符合[最佳实践](CONTRIBUTING.md#最佳实践)要求
- [ ] 我已测试预制件可以正常工作

## 版本说明

（可选）请简要描述此版本的变更内容或新增功能：

```
在这里描述你的变更...
```

## 额外信息

（可选）任何其他需要审核者知道的信息：

---

**注意事项：**
- 自动化检查会验证：JSON 格式、字段完整性、URL 可达性、manifest 一致性
- 请确保所有检查通过后再请求人工审核
- 审核通过后，预制件将自动部署到平台


# 当前 Unity 网页版 `you_bl` 替换案例

当前雀魂网页使用 Unity WebGL，不再请求旧版的
`charactor/you_BL/spine/*`。本案例直接替换“柚·足见独白”的当前
Unity AssetBundle。静态界面使用：

- `myassets/deco/character/you_bl/full/full.png`
- `myassets/deco/character/you_bl/bighead/bighead.png`

大厅动态展示使用：

- `myassets/spine/405906/you_bl.skel.txt`
- `myassets/spine/405906/you_bl.atlas.txt`
- `myassets/spine/405906/you_bl.png`

动态资源被替换为 Spine `4.2.08` 的单骨骼静态案例，并保留原皮肤的
`celebrate`、`celebrate_idle`、`click`、`greeting`、`idle` 动画名。

## 重新生成

使用单独的构建环境即可；MajsoulMax 运行时不需要 UnityPy：

```powershell
python -m pip install -r .\replace\unity\you_bl\requirements.txt
python .\replace\unity\you_bl\build_you_bl.py
```

默认输入为 `gys-transparent.png`，生成：

- `preview-full.png`（1114×1311）
- `preview-bighead.png`（256×256）
- `preview-spine-page.png`（2048×2048）
- `preview-spine.skel.txt` 与 `preview-spine.atlas.txt`
- `replace/assetbundles/DXT/*.majset` 四个资源包及一份尺寸清单

`source/` 保存当前版本的原包模板及 BundleInfoSO 清单。游戏更新后若
URL 哈希或 Bundle 结构变化，需要重新提取模板并更新
`build_you_bl.py` 中的文件名。

## 加载方法

1. 确认 `config/settings.yaml` 中 `replace: true`。
2. 将 `settings.replace.example.yaml` 的内容复制到
   `config/settings.replace.yaml`，然后重新启动 MajsoulMax。
3. 使用带 `--proxy-server=http://127.0.0.1:23410` 的隔离 Chrome。
4. 在开发者工具 Application → Storage 中执行 **Clear site data**，
   清掉 HTTP 缓存和 Unity 使用的 IndexedDB 持久化资源；仅勾选
   Network → **Disable cache** 可能无法清除已经保存的 AssetBundle。
5. 在游戏中选择“柚·足见独白”。

终端出现对应的 `已替换(replace)` 才表示浏览器实际请求并收到了新包；
通常会看到尺寸清单、立绘/头像包以及 Spine 数据/贴图包共五条记录。

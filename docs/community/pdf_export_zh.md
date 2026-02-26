# PDF 导出

## 用途

PDF 导出功能使用 MkDocs 及 `mkdocs-to-pdf` 插件，将完整的 Ragas 文档构建为单个 PDF 文件。

## 使用方式

实现采用两套独立的 MkDocs 配置：

- `mkdocs.yml`：用于标准 HTML 构建（无需 PDF 相关依赖）
- `mkdocs-pdf.yml`：继承主配置并启用 PDF 插件

构建 PDF 文档：

```bash
make build-docs-pdf
```

生成的 PDF 将位于 `site/pdf/document.pdf`。

仅构建 HTML 文档：

```bash
make build-docs
```

`make build-docs-pdf` 会在构建前自动检查系统依赖。

## PDF 中的 Mermaid 图表（离线）

Mermaid 图表在 PDF 构建过程中**离线**渲染（在 WeasyPrint 运行前先转换为 SVG），因此除 WeasyPrint 外还需一些额外依赖。

### 所需工具

- Node.js（用于运行 Mermaid 相关工具）
- Mermaid CLI（`mmdc`），通过 `@mermaid-js/mermaid-cli` 安装
- 供 Puppeteer 使用的无头浏览器（推荐：`chrome-headless-shell`）

## 当前限制

**系统依赖**：WeasyPrint 依赖各操作系统特定的系统库（Pango、Cairo），需单独安装。若遇问题，请参考 [WeasyPrint 安装说明](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html) 与 [故障排除指南](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#troubleshooting)。

**ReadTheDocs**：当前 ReadTheDocs 的构建配置中未启用 PDF 生成。

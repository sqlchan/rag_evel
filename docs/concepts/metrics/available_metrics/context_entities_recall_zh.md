## 上下文实体召回

`ContextEntityRecall` 根据 `reference` 与 `retrieved_contexts` 中共有实体数相对 `reference` 中实体数的比例，衡量检索上下文的实体召回。简言之，即 reference 中有多少比例的实体被召回。适用于旅游咨询、历史问答等以事实为主的场景，可评估检索机制在实体上的表现。

使用两个集合：  
- **$RE$**：reference 中的实体集合。  
- **$RCE$**：检索上下文中的实体集合。

公式：

$$
\text{Context Entity Recall} = \frac{\text{$RCE$ 与 $RE$ 的公共实体数}}{\text{$RE$ 中实体总数}}
$$

### 示例

（代码与原文一致，见 [context_entities_recall.md](context_entities_recall.md)。）

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

### 计算方式

将 reference 与检索上下文中的实体分别找出，再按上述公式计算。若两个检索机制在同一批文档上得到不同检索结果，在重视实体的场景下可比较哪个机制实体召回更好。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。

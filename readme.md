## This is @RAGF-01

描述：（待补充

---

## 前端

一个基于 Vue 3 和 TDesign 组件库开发的前端，主要提供处理文档解析，知识库管理，知识图谱生成，RAG 检索，Ollama 服务管理，智能问答的UI界面

- **前端框架**：Vue 3 + TypeScript
- **UI 组件库**：TDesign Vue Next
- **构建工具**：Vite
- **CSS 框架**：Tailwind CSS

### 运行（前端）

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```



## 后端

基于 FastAPI  提供服务的 RAG (检索增强生成) 后端服务，用于处理文档解析，知识库管理，知识图谱生成，RAG 检索，向量存储，Ollama 服务管理，智能问答。

### 运行（后端）

```bash
# 创建虚拟环境
python -m venv venv
# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

#启动fastapi服务
python main.py --host 0.0.0.0 --port 8000 --reload
```






---

### Contributors 📋

*Thanks goes to these wonderful people:*

<table border="1" cellpadding="10" cellspacing="0" width="100%" align="center">
    <tr>
        <td align="center" valign="top">
            <a href="https://github.com/Zhongye1">
                <img src="https://avatars.githubusercontent.com/u/145737758?v=4" alt="Vaibhav" width="100" height="100" border="0" />
                <br />
                <strong>Gotoh Hitori</strong>
                <br />
                <em>GitHub: <a href="https://github.com/Zhongye1">@Zhongye1</a></em>
                <br />
                Contributions: <br>代码 💻 <br>写文档 📖
            </a>
        </td>
        <td align="center" valign="top">
            <a href="https://github.com/ourcx">
                <img src="https://avatars.githubusercontent.com/u/173872687?v=4" alt="褚喧" width="100" height="100" border="0" />
                <br />
                <strong>褚喧</strong>
                <br />
                <em>GitHub: <a href="https://github.com/ourcx">@ourcx</a></em>
                <br />
                Contributions: 正在贡献
            </a>
        </td>
        <td align="center" valign="top">
            <a href="https://github.com/haha-1205">
                <img src="https://avatars.githubusercontent.com/u/222571036?s=400&u=254ac083b4d85e08dc7dee9d186624dfaa031614&v=4" alt="ZXT" width="100" height="100" border="0" />
                <br />
                <strong>ZXT</strong>
                <br />
                <em>GitHub: <a href="https://github.com/haha-1205">@haha-1205</a></em>
                <br />
                Contributions: 贡献
            </a>
        </td>
        <td align="center" valign="top">
            <a href="https://github.com/HJX">
                <img src="https://pica.zhimg.com/80/v2-3293674e35c7d8cf2040db9121bc559c_720w.webp" alt="HJX" width="100" height="100" border="0" />
                <br />
                <strong>HJX</strong>
                <br />
                <em>GitHub: <a href="https://github.com/HJX">@HJX</a></em>
                <br />
                Contributions: 
            </a>
        </td>
        <td align="center" valign="top">
            <a href="https://github.com/z1pperexplorer">
                <img src="https://avatars.githubusercontent.com/u/222624613?s=400&u=3778bd14e4e096302f3677074fe9c07545b18467&v=4" alt="A1r" width="100" height="100" border="0" />
                <br />
                <strong>A1r</strong>
                <br />
                <em>GitHub: <a href="https://github.com/z1pperexplorer">@z1pperexplorer</a></em>
                <br />
                Contributions: Contributing
            </a>
        </td>
    </tr>
</table>



## 详细介绍

讲一下前后端技术栈，代码结构，架构（最好画图），各页面各功能各接口








## # 后续开发

1. ~~实现用户认证和权限管理~~
2. ~~添加模型支持和参数配置~~
3. ~~实现文件处理能力，支持更多格式~~
4. ~~知识库管理：完整的知识库 CRUD 操作，支持文件上传、管理和检索测试。~~
5. ~~搜索功能：支持多语言环境下的文档检索，包括自动语言检测。~~
6. ~~分页和批量操作：针对大量文档提供高效的管理界面。~~
7. 实现文档协作功能
8. 打包并支持 docker 部署
9. 其余需求补充
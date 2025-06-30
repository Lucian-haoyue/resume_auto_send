# LangChain AI 求职邮件助手 (V2.0)

[](https://www.python.org/)
[](https://opensource.org/licenses/MIT)

这是一个基于大型语言模型（LLM）和LangChain框架的自动化求职工具。它能够根据你提供的个人简历、邮件模板和目标岗位的描述（JD），自动生成一封高度个性化、亮点突出、格式专业的求职邮件，并将其连同你的PDF简历作为附件，自动发送到招聘方的邮箱。

**V2.0 版本核心亮点：附件名称会根据生成的邮件主题动态变化，更显专业！**

-----

## 🚀 主要功能

  * **AI精准匹配**：利用LLM（本项目使用DeepSeek）深度分析岗位JD，从你的简历中提取最相关的技能和经验，生成高度匹配的邮件内容。
  * **个性化内容生成**：自动在邮件正文中突出你与岗位最契合的2-3个核心优势，告别千篇一律的模板。
  * **全流程自动化**：从内容生成到邮件发送，实现端到端自动化。只需粘贴目标JD，即可一键完成申请。
  * **动态附件命名**：智能地将邮件主题作为PDF简历附件的名称（如 `应聘数据分析师-张三.pdf`），让你的申请在众多邮件中脱颖而出，彰显专业性。
  * **高度可配置**：通过简单的配置文件，轻松更换你的简历、邮件模板和发件人信息。

## 🛠️ 技术栈

  * **Python 3.9+**
  * **LangChain & LangChain-OpenAI**: 核心的LLM编排与调用框架。
  * **DeepSeek API**: 提供强大的内容生成能力。
  * **python-dotenv**: 用于管理环境变量，保护敏感信息。
  * **smtplib**: Python标准库，用于发送邮件。

## ⚙️ 如何使用

请遵循以下步骤来配置和运行本项目：

### 1\. 克隆项目到本地

```bash
git clone https://github.com/your-username/your-repository-name.git
cd your-repository-name
```

### 2\. 安装依赖

建议创建一个虚拟环境。项目依赖已在 `requirements.txt` 中列出。

```bash
# 创建并激活虚拟环境 (可选，但推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装所有必需的库
pip install -r requirements.txt
```

*(如果项目中没有 `requirements.txt` 文件，请根据代码中的 `import` 手动安装，主要包括 `langchain`, `langchain-openai`, `python-dotenv`)*

### 3\. 配置项目文件

这是最关键的一步，你需要准备以下文件和信息：

#### a) 创建 `.env` 环境变量文件

在项目根目录下创建一个名为 `.env` 的文件。它用于存放你的敏感信息。文件内容请参考以下模板：

```env
# 你的发件邮箱账号 (例如，163邮箱)
SENDER_EMAIL="your_email@163.com"

# 你的发件邮箱的SMTP授权码 (注意：不是邮箱登录密码！)
SENDER_PASSWORD="your_email_app_password"

# 你申请的DeepSeek API Key
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
```

#### b) 准备个人文件

请将以下三个文件放入指定的文件夹或路径中，并**确保更新代码中的文件路径变量**：

1.  **邮件内容模板.txt (`TEMPLATE_PATH`)**:

      * 一个包含你通用求职信内容的文本文件。你可以使用占位符，让AI来填充关键部分。

2.  **你的简历.md (`RESUME_TEXT_PATH`)**:

      * 一份Markdown或纯文本格式的简历。这份简历将作为“知识库”提供给LLM，让它了解你的背景和技能。**内容越详细、结构化，AI生成的内容越精准。**

3.  **你的PDF简历.pdf (`PDF_RESUME_PATH`)**:

      * 这是最终将作为附件发送的PDF文件。请确保文件名简洁明了。

修改代码 `main.py` 文件开头的全局配置部分，将文件路径更新为你自己电脑上的绝对或相对路径。

```python
# --- 1. 全局配置 (请根据你的情况修改此部分) ---

# ...

# 文件路径配置
TEMPLATE_PATH = r"path/to/你的/邮件内容模板.txt"
RESUME_TEXT_PATH = r"path/to/你的/简历.md" 
PDF_RESUME_PATH = r"path/to/你的/简历.pdf" 
```

### 4\. 运行脚本

一切准备就绪后，在终端中运行主程序：

```bash
python main.py  # 假设你的主文件名是 main.py
```

程序启动后，会提示你粘贴目标岗位的JD。将完整的岗位描述粘贴进去，然后按回车键，自动化流程便会启动。

## 📄 代码结构解析

  * `main.py`: 项目主文件，包含了所有逻辑。
      * **全局配置**: 设定所有文件路径和关键变量。
      * **邮件发送模块 (`send_final_email`)**: 负责构建并发送邮件。此模块包含动态生成附件名的逻辑。
      * **LangChain内容生成模块**: 定义了与LLM交互的Prompt模板、模型实例和输出解析器。
      * **自动化链构建**: 使用 `|` (管道) 操作符将各个模块串联成一个完整的执行链。
      * **主程序入口 (`if __name__ == "__main__":`)**: 负责加载文件、接收用户输入并调用执行链。

## ⚠️ 注意事项

1.  **SMTP配置**：本代码默认使用`smtp.163.com`作为SMTP服务器。如果你使用其他邮箱（如QQ、Gmail），需要修改`send_final_email`函数中的服务器地址和端口号。
2.  **邮箱授权码**：`SENDER_PASSWORD`应为邮箱服务商提供的**SMTP授权码**，而不是你的邮箱登录密码。请自行前往你的邮箱设置中开启SMTP服务并获取授权码。
3.  **API Key安全**：切勿将你的`.env`文件或包含API Key的代码上传到公开的GitHub仓库。`.gitignore`文件中应始终包含`.env`。
4.  **文件路径**：强烈建议检查并修改代码中的文件路径，确保程序能正确找到你的个人文件。

## 许可

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 授权。
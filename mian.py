import os
import json
import smtplib
import re 
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# --- 1. 全局配置 (请根据你的情况修改此部分) ---

load_dotenv()

# [重要] 文件路径配置
# 建议在项目根目录下创建一个名为 'config' 的文件夹, 
# 然后将你的模板文件和简历文件放入其中, 并更新下面的文件名。
CONFIG_DIR = "config" 
TEMPLATE_PATH = os.path.join(CONFIG_DIR, "email_template.txt")       # 你的邮件模板文件
RESUME_TEXT_PATH = os.path.join(CONFIG_DIR, "my_resume_template.md")  # 用于LLM分析的简历文本 (Markdown或TXT格式)
PDF_RESUME_PATH = os.path.join(CONFIG_DIR, "my_resume.pdf")           # 作为附件发送的最终版简历PDF


# --- 2. 邮件发送模块 (功能不变, 逻辑已优化) ---
def send_final_email(chain_output: dict):
    """
    接收LangChain链的输出，并调用SMTP逻辑发送最终邮件。
    附件名称将根据邮件主题动态生成。
    """
    print("\n--- 进入邮件发送模块 ---")
    
    subject = chain_output.get('subject')
    receiver_email = chain_output.get('recipient_email')
    body_html = chain_output.get('body')

    if not receiver_email or receiver_email == 'not_found':
        message = "邮件发送中止：模型未能从岗位描述中提取到收件人邮箱。"
        print(f"❌ {message}")
        return {"status": "error", "message": message}

    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not all([subject, body_html, sender_email, sender_password]):
        message = "邮件发送中止：缺少必要的邮件信息或发件人凭证。"
        print(f"❌ {message}")
        return {"status": "error", "message": message}
    
    # [新功能] 根据邮件主题动态生成附件名
    # 1. 清洗主题，移除不能用于文件名的特殊字符
    sanitized_subject = re.sub(r'[\\/*?:"<>|]', "", subject)
    # 2. 加上.pdf后缀
    dynamic_attachment_name = f"{sanitized_subject}.pdf"
    print(f"ℹ️ 动态生成附件名: {dynamic_attachment_name}")


    # --- 开始构建邮件 ---
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html", "utf-8"))

    # 附加PDF简历
    try:
        with open(PDF_RESUME_PATH, "rb") as file:
            attachment = MIMEApplication(file.read(), _subtype="pdf")
            # [修改点] 使用动态生成的附件名
            attachment.add_header('Content-Disposition', 'attachment', filename=dynamic_attachment_name)
            message.attach(attachment)
            print(f"✅ 附件 '{dynamic_attachment_name}' 已成功添加。")
    except FileNotFoundError:
        message = f"邮件发送中止：未找到附件文件 {PDF_RESUME_PATH}"
        print(f"❌ {message}")
        return {"status": "error", "message": message}
    except Exception as e:
        message = f"邮件发送中止：添加附件时发生错误: {e}"
        print(f"❌ {message}")
        return {"status": "error", "message": message}

    # 连接SMTP服务器并发送
    try:
        print(f"正在尝试连接 smtp.163.com 并发送邮件至 {receiver_email}...")
        with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        success_message = f"邮件已成功发送至 {receiver_email}！"
        print(f"🎉 {success_message}")
        return {"status": "success", "message": success_message}
    except Exception as e:
        error_message = f"邮件发送失败：{e}"
        print(f"❌ {error_message}")
        return {"status": "error", "message": error_message}

# --- 3. LangChain 内容生成模块 (保持不变) ---
prompt_template_str = """
role: 你是一位专业的求职教练和精通HTML格式的文案专家。
task: 根据我提供的[邮件模板]、[我的简历]以及这个[岗位描述]，为我生成一封求职申请邮件所需的所有信息。
requirements:
  - 精准匹配: 深入分析[岗位描述]，从[我的简历]中找出最相关的经历、技能进行匹配展示。
  - 突出亮点: 在邮件正文中重点突出与岗位最契合的2-3个核心优势。
  - 避免编造: 严格基于我提供的简历内容，不要虚构或夸大事实。
output_format:
  非常重要: 你的最终输出必须是一个严格的、不包含任何其他解释或注释的JSON对象。该JSON对象必须包含以下三个键 (keys): subject, recipient_email, body。
  subject: (string) 根据我的简历和岗位描述，生成一个基于岗位描述要求的邮件主题。
  recipient_email: (string) 从[岗位描述]中精准提取招聘邮箱地址。如果找不到，请将此键的值设为 "not_found"。
  body: (string) 生成完整的邮件正文的HTML代码。请使用 <p>, <strong>, <ul>, <li>, <br> 等标签确保格式整齐。
---
邮件模板: '{email_template}'
我的简历: '{my_resume}'
岗位描述: '{job_description}'
---
**生成的 JSON 输出:**
"""
prompt = ChatPromptTemplate.from_template(prompt_template_str)
llm = ChatOpenAI(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com", temperature=0.5)
output_parser = JsonOutputParser()

# --- 4. 构建完整的自动化链 (保持不变) ---
final_chain = prompt | llm | output_parser | send_final_email

# --- 5. 执行主程序 (保持不变) ---
if __name__ == "__main__":
    print("--- 自动化求职申请端到端流程 (V2: 附件名与主题同步) ---")
    
    def read_file_content(file_path: str) -> str | None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read()
        except Exception as e:
            print(f"错误：读取文件 {file_path} 失败: {e}")
            return None

    print("正在加载简历和邮件模板...")
    email_template_content = read_file_content(TEMPLATE_PATH)
    resume_text_content = read_file_content(RESUME_TEXT_PATH)

    if email_template_content is None or resume_text_content is None:
        print("因文件加载失败，程序已中止。")
        exit()
    
    print("文件加载成功！\n")

    job_description_input = input("请将目标岗位的JD（岗位描述）完整粘贴到此处，然后按回车键执行完整流程：\n")

    if not job_description_input.strip():
        print("错误：岗位描述不能为空。")
        exit()

    print("\n==================================================")
    print("🚀 流程启动：正在生成内容并准备发送邮件...")
    print("==================================================\n")

    try:
        final_result = final_chain.invoke({
            "email_template": email_template_content,
            "my_resume": resume_text_content,
            "job_description": job_description_input
        })
        
        print("\n------------------ 流程执行完毕 ------------------")
        print(f"最终状态: {final_result.get('status')}")
        print(f"最终信息: {final_result.get('message')}")
        print("----------------------------------------------------")

    except Exception as e:
        print(f"\n❌ 在执行LangChain链的过程中发生严重错误: {e}")
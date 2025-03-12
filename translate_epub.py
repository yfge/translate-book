import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import time
import openai  # 替换 deepseek 导入
import os
import argparse
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
class EpubTranslator:
    def __init__(self):
        self.openai_client = openai.OpenAI()
    def translate_text(self, text):
        """使用 OpenAI API 翻译文本"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"正在翻译文本: {text[:50]}...")  # 添加调试信息
                response = self.openai_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a translator. Translate the following English text to Chinese. Keep the original formatting and only translate the text."},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.3
                )
                translated = response.choices[0].message.content.strip()
                print(f"翻译结果: {translated[:50]}...")  # 添加调试信息
                return translated
            except Exception as e:
                print(f"尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")  # 详细的错误信息
                if attempt == max_retries - 1:
                    print(f"翻译最终失败: {e}")
                    return text
                time.sleep(5)  # 增加重试等待时间
    
    def process_html_content(self, html_content):
        """处理 HTML 内容，只翻译实际文本内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 定义需要跳过的标签
        skip_tags = {'script', 'style', 'code', 'pre', 'head', 'nav', 'meta'}
        
        def should_translate(text):
            """判断文本是否需要翻译"""
            text = text.strip()
            
            # 跳过空白文本
            if not text:
                return False
                
            # 跳过 XML/HTML 声明和指令
            if text.startswith('<?') or text.startswith('<!') or text.startswith('<?xml'):
                return False
                
            # 跳过纯数字
            if text.isdigit():
                return False
                
            # 跳过 HTML 标签相关内容
            if any(text.startswith(prefix) for prefix in ['<', '{', '/', '=']):
                return False
                
            # 跳过常见的 HTML/XML 属性和值
            skip_words = {
                'xml', 'version', 'encoding', 'utf-8', 'html', 'xmlns', 
                'http', 'www', 'org', 'opf', 'dc', 'meta', 'content', 
                'class', 'id', 'style', 'src', 'href', 'alt', 'title'
            }
            if text.lower() in skip_words:
                return False
            
            # 跳过 XML 声明和属性组合
            if "xml version=" in text.lower() or "encoding=" in text.lower():
                return False
                
            # 跳过没有英文字母的文本
            if not any(c.isascii() and c.isalpha() for c in text):
                return False
                
            # 跳过很短的文本
            if len(text) <= 1:
                return False
                
            # 跳过看起来像文件路径或URL的文本
            if '/' in text or '\\' in text or '.com' in text or '.org' in text:
                return False
                
            # 跳过看起来像代码或配置的文本
            if ':' in text and not any(c.isspace() for c in text):
                return False
            
            return True
        
        def process_node(node):
            """递归处理节点"""
            # 如果是文本节点
            if isinstance(node, str):
                text = node.strip()
                if should_translate(text):
                    try:
                        translated = self.translate_text(text)
                        return translated
                    except Exception as e:
                        print(f"翻译文本时出错: {text[:50]}... - {e}")
                        return node
                return node
            
            # 如果是需要跳过的标签
            if node.name in skip_tags:
                return
            
            # 处理子节点
            for child in node.children:
                if isinstance(child, str):
                    if should_translate(child.strip()):
                        try:
                            translated = self.translate_text(child.strip())
                            child.replace_with(translated)
                        except Exception as e:
                            print(f"翻译文本时出错: {child[:50]}... - {e}")
                else:
                    process_node(child)
        
        # 开始处理
        for node in soup.children:
            process_node(node)
        
        return str(soup)

    def translate_epub(self, input_path, output_path):
        """翻译整本 epub 书籍"""
        try:
            # 读取原始 epub
            print(f"正在读取 epub 文件: {input_path}")
            book = epub.read_epub(input_path)
            
            # 创建新的 epub
            new_book = epub.EpubBook()
            
            # 复制元数据
            try:
                # 获取原书的标识符
                identifiers = book.get_metadata('DC', 'identifier')
                if identifiers:
                    new_book.set_identifier(identifiers[0][0])
                else:
                    new_book.set_identifier('id_' + str(time.time()))
                
                # 获取原书的标题
                titles = book.get_metadata('DC', 'title')
                if titles:
                    title = titles[0][0]
                else:
                    title = "未知标题"
                print(f"正在处理书籍: {title}")
                new_book.set_title(f"{title} (中文译本)")
                
                # 设置语言
                new_book.set_language('zh')
                
                # 复制其他元数据（可选）
                for creator in book.get_metadata('DC', 'creator'):
                    new_book.add_metadata('DC', 'creator', creator[0])
                
            except Exception as e:
                print(f"处理元数据时出错: {e}")
                # 设置默认元数据
                new_book.set_identifier('id_' + str(time.time()))
                new_book.set_title("翻译书籍")
                new_book.set_language('zh')
            
            # 复制并翻译所有项目
            new_items = []
            total_items = len(list(book.get_items()))
            for i, item in enumerate(book.get_items(), 1):
                print(f"正在处理第 {i}/{total_items} 个项目...")
                if isinstance(item, epub.EpubHtml):
                    print(f"翻译 HTML 内容: {item.get_name()}")
                    # 处理 HTML 内容
                    new_item = epub.EpubHtml(
                        uid=item.get_id(),
                        file_name=item.get_name(),
                        media_type='application/xhtml+xml'
                    )
                    new_content = self.process_html_content(item.get_content().decode('utf-8'))
                    new_item.set_content(new_content.encode('utf-8'))
                    new_items.append(new_item)
                else:
                    # 直接复制其他资源（图片等）
                    new_items.append(item)
            
            # 添加所有项目到新书
            for item in new_items:
                new_book.add_item(item)
            
            # 复制目录结构
            new_book.toc = book.toc
            new_book.spine = book.spine
            
            # 保存新的 epub
            epub.write_epub(output_path, new_book)
            print(f"翻译完成！已保存到: {output_path}")
        except Exception as e:
            print(f"翻译过程中出错: {e}")

def main():
    # 设置你的 OpenAI API key
    """主函数，处理命令行参数"""
    parser = argparse.ArgumentParser(description='翻译 EPUB 文件')
    parser.add_argument('input_file', help='输入的 EPUB 文件路径')
    parser.add_argument('output_file', nargs='?', help='输出的 EPUB 文件路径 (可选)')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    
    # 如果未提供输出文件路径，则在当前目录下创建一个默认名称
    if args.output_file:
        output_file = args.output_file
    else:
        input_path = Path(input_file)
        output_file = f"{input_path.stem}_translated{input_path.suffix}"

    
    translator = EpubTranslator()
    translator.translate_epub(input_file, output_file)
    print(f"翻译完成！已保存到: {output_file}")

if __name__ == "__main__":
    main() 
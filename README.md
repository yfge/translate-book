# EPUB 翻译工具

这是一个使用 OpenAI API 将英文 EPUB 电子书翻译成中文的工具。它能保持原书的格式和结构，同时智能地只翻译实际的文本内容。

## 功能特点

- 保持原始 EPUB 文件的格式和结构
- 智能识别并仅翻译实际文本内容
- 保留原书的图片、样式和其他资源
- 自动跳过代码、脚本等技术内容
- 支持命令行参数
- 使用 OpenAI API 进行高质量翻译

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yfge/epub-translator.git
cd epub-translator
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置 OpenAI API 密钥：
```bash
cp .env.example .env
```

## 使用方法

### 命令行翻译

```bash
python translate_epub.py <input_file> [output_file]
```

示例：
```bash
python translate_epub.py BraveNewWords.epub
```

### 注意事项


1. 确保你有足够的 API 额度，因为翻译一本书可能需要大量的 API 调用
2. 翻译过程可能需要较长时间，具体取决于书的大小
3. 建议先用小文件测试
4. 请遵守版权法规和 API 使用条款


## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

MIT License

## 免责声明

本工具仅供学习和研究使用。请确保你有合法的权利翻译相关内容。作者不对使用本工具产生的任何问题负责。
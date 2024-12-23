# 亚马逊评论爬虫 GUI

这是一个基于Flet和Selenium的亚马逊产品评论爬虫GUI应用,可以爬取带有图片和视频的评论,并将数据保存为Excel文件。

## 功能特点

- 图形用户界面,操作简单直观
- 支持多种评论筛选条件:
  - 排序方式(默认/最新/最有帮助)
  - 评论类型(所有/已验证购买)
  - 评分筛选(1-5星/正面/负面)
  - 商品规格(所有/当前规格)
  - 评论内容(所有/仅含图片视频)
  - 关键词搜索
- 自动提取评论中的图片和视频
- 支持提取用户信息(用户名、头像)
- 获取评论的详细信息(评分、标题、内容、日期等)
- 支持提取商品颜色和尺寸信息
- 自动处理已验证购买标识
- 使用Chrome浏览器配置文件保存登录状态
- 随机延迟请求以避免被封

## 安装要求

- Python 3.8+
- Chrome浏览器
- 虚拟环境(推荐)

## 依赖包

```bash
flet>=0.21.0
selenium
beautifulsoup4
pandas
webdriver_manager
```

## 安装步骤

1. 创建并激活虚拟环境:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行GUI应用:
```bash
python main.py
```

2. 在GUI界面中:
   - 输入产品ID(从亚马逊产品URL中获取,如B07XNZHZ58)
   - 设置要爬取的页数
   - 选择筛选条件
   - 首次运行时取消勾选"无头模式",以便手动登录亚马逊账号
   - 点击"开始爬取"按钮

3. 程序会自动开始爬取,并在完成后将结果保存为Excel文件

## 数据输出

脚本会生成一个Excel文件,包含以下字段:
- 用户名
- 用户头像
- 评分
- 标题
- 评论内容
- 评论时间
- 颜色
- 尺寸
- 已验证购买
- 评论图片
- 评论视频

## 注意事项

- 首次运行时需要手动登录亚马逊账号
- 建议设置适当的爬取间隔,避免频繁请求
- 产品ID可以从亚马逊产品URL中获取,通常是类似"B07XNZHZ58"的格式
- 确保Chrome浏览器已正确安装
- 如遇到反爬验证,请适当调整延迟时间

## 常见问题

1. 如何获取产品ID？
   - 在亚马逊产品页面URL中找到类似"B07XNZHZ58"的字符串

2. 为什么需要登录？
   - 亚马逊对未登录用户的评论访问有限制
   - 登录后可以访问更多评论内容和媒体文件

3. 如何处理反爬验证？
   - 增加随机延迟时间
   - 确保使用正确的User-Agent
   - 避免频繁请求


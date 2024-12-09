import flet as ft
import os
from amazon_review_scraper import AmazonReviewScraper
import re

class AmazonReviewScraperApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_controls()
        self.add_controls()
        
    def setup_page(self):
        self.page.title = "亚马逊评论爬虫"
        self.page.window_width = 800
        self.page.window_height = 800
        self.page.window_resizable = False
        self.page.window_center = True
        self.page.window_top = 50  # 设置窗口距离屏幕顶部的距离为50像素
        self.page.window_always_on_top = True  # 设置窗口始终置顶
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 30
        self.page.scroll = ft.ScrollMode.AUTO
        self.page.update()

    def setup_controls(self):
        # 标题
        self.title = ft.Text(
            "亚马逊评论爬虫", 
            size=32, 
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
        
        # 产品ID输入框
        self.product_id = ft.TextField(
            label="产品ID",
            hint_text="请输入亚马逊产品ID (例如: B07XNZHZ58)",
            width=400,
            prefix_icon=ft.icons.SHOPPING_CART,
            helper_text="在亚马逊产品页面URL中找到类似'B07XNZHZ58'的字符串"
        )
        
        # 页数输入框
        self.pages = ft.TextField(
            label="爬取页数",
            hint_text="请输入要爬取的评论页数",
            width=400,
            prefix_icon=ft.icons.NUMBERS,
            helper_text="每页大约10条评论",
            value="1"
        )
        
        # 搜索条件区域标题
        self.filter_title = ft.Text(
            "搜索条件", 
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.BLUE_700
        )
        
        # 排序方式
        self.sort_dropdown = ft.Dropdown(
            label="排序方式",
            hint_text="选择评论排序方式",
            width=400,
            options=[
                ft.dropdown.Option("default", "默认排序"),
                ft.dropdown.Option("recent", "最新评论"),
                ft.dropdown.Option("helpful", "最有帮助")
            ],
            value="default"
        )
        
        # 评论类型
        self.reviewer_type_dropdown = ft.Dropdown(
            label="评论类型",
            hint_text="选择评论类型",
            width=400,
            options=[
                ft.dropdown.Option("all_reviews", "所有评论"),
                ft.dropdown.Option("avp_only_reviews", "已验证购买的评论")
            ],
            value="all_reviews"
        )
        
        # 评分筛选
        self.star_filter_dropdown = ft.Dropdown(
            label="评分筛选",
            hint_text="选择评分范围",
            width=400,
            options=[
                ft.dropdown.Option("all_stars", "全部评价"),
                ft.dropdown.Option("five_star", "五星评价"),
                ft.dropdown.Option("four_star", "四星评价"),
                ft.dropdown.Option("three_star", "三星评价"),
                ft.dropdown.Option("two_star", "二星评价"),
                ft.dropdown.Option("one_star", "一星评价"),
                ft.dropdown.Option("positive", "正面评价"),
                ft.dropdown.Option("critical", "负面评价")
            ],
            value="all_stars"
        )
        
        # 商品规格
        self.format_type_dropdown = ft.Dropdown(
            label="商品规格",
            hint_text="选择商品规格",
            width=400,
            options=[
                ft.dropdown.Option("all_formats", "所有规格"),
                ft.dropdown.Option("current_format", "当前规格")
            ],
            value="all_formats"
        )
        
        # 评论内容
        self.media_type_dropdown = ft.Dropdown(
            label="评论内容",
            hint_text="选择评论内容类型",
            width=400,
            options=[
                ft.dropdown.Option("all_contents", "所有评论"),
                ft.dropdown.Option("media_reviews_only", "仅含图片/视频")
            ],
            value="all_contents"
        )
        
        # 关键词搜索
        self.keyword_search = ft.TextField(
            label="关键词搜索",
            hint_text="输入要搜索的关键词",
            width=400,
            prefix_icon=ft.icons.SEARCH,
            helper_text="搜索评论内容中包含的关键词"
        )
        
        # 无头模式选择
        self.headless_mode = ft.Checkbox(
            label="无头模式运行",
            value=False
        )
        # 无头模式说明文本
        self.headless_mode_helper = ft.Text(
            "首次运行请取消勾选，以便手动登录亚马逊账号",
            size=12,
            color=ft.colors.GREY_700,
            italic=True
        )
        
        # 开始按钮
        self.start_button = ft.ElevatedButton(
            "开始爬取",
            width=400,
            icon=ft.icons.DOWNLOAD,
            on_click=self.start_scraping
        )
        
        # 状态文本
        self.status_text = ft.Text(
            size=16,
            color=ft.colors.GREY_700
        )
        
        # 进度条
        self.progress_bar = ft.ProgressBar(
            width=400,
            visible=False
        )

    def add_controls(self):
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        self.title,
                        ft.Container(height=20),
                        self.product_id,
                        ft.Container(height=10),
                        self.pages,
                        ft.Container(height=20),
                        self.filter_title,
                        ft.Container(height=10),
                        self.sort_dropdown,
                        ft.Container(height=10),
                        self.reviewer_type_dropdown,
                        ft.Container(height=10),
                        self.star_filter_dropdown,
                        ft.Container(height=10),
                        self.format_type_dropdown,
                        ft.Container(height=10),
                        self.media_type_dropdown,
                        ft.Container(height=10),
                        self.keyword_search,
                        ft.Container(height=20),
                        self.headless_mode,
                        self.headless_mode_helper,
                        ft.Container(height=20),
                        self.start_button,
                        ft.Container(height=10),
                        self.progress_bar,
                        self.status_text,
                        ft.Container(height=30),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=ft.padding.only(bottom=30),
            )
        )

    def validate_inputs(self):
        # 验证产品ID
        if not self.product_id.value:
            self.product_id.error_text = "请输入产品ID"
            self.page.update()
            return False
        
        # 验证产品ID格式
        if not re.match(r'^B[0-9A-Z]{9}$', self.product_id.value):
            self.product_id.error_text = "产品ID格式不正确"
            self.page.update()
            return False
        
        # 验证页数
        try:
            pages = int(self.pages.value)
            if pages < 1:
                raise ValueError
            self.pages.error_text = None
        except:
            self.pages.error_text = "请输入有效的页数"
            self.page.update()
            return False
            
        return True

    def start_scraping(self, e):
        if not self.validate_inputs():
            return
        
        # 禁用输入控件
        self.disable_controls()
        
        # 开始爬取
        try:
            self.status_text.value = "正在初始化爬虫..."
            self.progress_bar.visible = True
            self.page.update()
            
            # 创建爬虫实例
            scraper = AmazonReviewScraper(headless=self.headless_mode.value)
            
            try:
                # 开始爬取
                self.status_text.value = "正在爬取评论..."
                self.page.update()
                
                # 构建URL参数
                url_params = self.build_url_params()
                
                reviews = scraper.get_reviews(
                    self.product_id.value, 
                    int(self.pages.value),
                    url_params=url_params
                )
                
                if reviews:
                    # 保存结果
                    output_file = f'amazon_reviews_{self.product_id.value}.xlsx'
                    scraper.save_to_excel(reviews, output_file)
                    
                    self.status_text.value = f"爬取完成！共获取{len(reviews)}条评论\n结果已保存至: {output_file}"
                    self.status_text.color = ft.colors.GREEN_700
                else:
                    self.status_text.value = "未找到评论或爬取失败"
                    self.status_text.color = ft.colors.RED_700
                    
            except Exception as e:
                self.status_text.value = f"爬取过程中出错: {str(e)}"
                self.status_text.color = ft.colors.RED_700
                
            finally:
                scraper.close()
                
        except Exception as e:
            self.status_text.value = f"初始化爬虫失败: {str(e)}"
            self.status_text.color = ft.colors.RED_700
            
        finally:
            # 恢复输入控件
            self.enable_controls()
            self.progress_bar.visible = False
            self.page.update()
            
    def disable_controls(self):
        self.product_id.disabled = True
        self.pages.disabled = True
        self.headless_mode.disabled = True
        self.start_button.disabled = True
        self.sort_dropdown.disabled = True
        self.reviewer_type_dropdown.disabled = True
        self.star_filter_dropdown.disabled = True
        self.format_type_dropdown.disabled = True
        self.media_type_dropdown.disabled = True
        self.keyword_search.disabled = True
        
    def enable_controls(self):
        self.product_id.disabled = False
        self.pages.disabled = False
        self.headless_mode.disabled = False
        self.start_button.disabled = False
        self.sort_dropdown.disabled = False
        self.reviewer_type_dropdown.disabled = False
        self.star_filter_dropdown.disabled = False
        self.format_type_dropdown.disabled = False
        self.media_type_dropdown.disabled = False
        self.keyword_search.disabled = False

    def build_url_params(self):
        params = {
            'ie': 'UTF8',
            'reviewerType': self.reviewer_type_dropdown.value,
            'pageNumber': '1'  # 初始页码
        }
        
        # 添加排序参数
        if self.sort_dropdown.value != "default":
            params['sortBy'] = self.sort_dropdown.value
            
        # 添加评分筛选
        if self.star_filter_dropdown.value != "all_stars":
            params['filterByStar'] = self.star_filter_dropdown.value
            
        # 添加商品规格
        if self.format_type_dropdown.value != "all_formats":
            params['formatType'] = self.format_type_dropdown.value
            
        # 添加评论内容类型
        if self.media_type_dropdown.value != "all_contents":
            params['mediaType'] = self.media_type_dropdown.value
            
        # 添加关键词搜索
        if self.keyword_search.value:
            params['filterByKeyword'] = self.keyword_search.value
            
        return params

def main(page: ft.Page):
    app = AmazonReviewScraperApp(page)

if __name__ == "__main__":
    ft.app(target=main)

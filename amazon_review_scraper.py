import time
import random
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

class AmazonReviewScraper:
    # 初始化
    def __init__(self, headless=False):
        # 初始化Chrome选项
        chrome_options = Options()

        # 设置为可视化或无头模式
        if headless:
            chrome_options.add_argument('--headless')
        
        # 设置User-Agent与语言
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
        chrome_options.add_argument('--lang=zh-CN')

         # 获取 Chrome Profile 路径
        root_dir = os.path.dirname(os.path.abspath(__file__))
        chrome_profile_path = os.path.join(root_dir, 'chrome_profile')

        # 设置用户数据目录，确保在此目录下可保存登录信息
        chrome_options.add_argument(f'--user-data-dir={chrome_profile_path}')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        
        # 避免被识别为自动化测试
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.month_map = {
            'January': '01', 'February': '02', 'March': '03',
            'April': '04', 'May': '05', 'June': '06',
            'July': '07', 'August': '08', 'September': '09',
            'October': '10', 'November': '11', 'December': '12'
        }
    # 关闭浏览器
    def close(self):
        self.driver.quit()
    
    # 解析评论日期
    def parse_review_date(self, date_text):
        try:
            pattern = r'Reviewed in (.*?) on (\w+) (\d{1,2}), (\d{4})'
            match = re.match(pattern, date_text)
            if match:
                country = match.group(1)
                month = self.month_map.get(match.group(2), '00')
                day = match.group(3).zfill(2)
                year = match.group(4)
                formatted_date = f"{year}-{month}-{day}"
                return f"{country} {formatted_date}"
            return date_text
        except Exception as e:
            print(f"日期解析错误 '{date_text}': {str(e)}")
            return date_text
    # 获取用户信息
    def get_user_info(self, review):
        try:
            profile_link = review.find('a', {'class': 'a-profile'})
            if profile_link:
                username = profile_link.find('span', {'class': 'a-profile-name'})
                username = username.text.strip() if username else ''
                avatar_div = profile_link.find('div', {'class': 'a-profile-avatar'})
                avatar_url = avatar_div.find('img')['src'] if avatar_div and avatar_div.find('img') else ''
                return {
                    'username': username,
                    'avatar_url': avatar_url
                }
            return {'username': '', 'avatar_url': ''}
        except Exception as e:
            print(f"获取用户信息时出错: {str(e)}")
            return {'username': '', 'avatar_url': ''}
    # 获取评论图片
    def get_review_images(self, review):
        try:
            images_div = review.find('div', {'class': 'cr-lightbox-image-thumbnails'})
            image_urls = []
            hd_image_urls = []
            if images_div:
                images = images_div.find_all('img', {'class': 'cr-lightbox-image-thumbnail'})
                for img in images:
                    thumb_url = img.get('src', '')
                    if thumb_url:
                        image_urls.append(thumb_url)
                        hd_url = thumb_url.replace('._SY88', '')
                        hd_image_urls.append(hd_url)
            return ';'.join(hd_image_urls)
        except Exception as e:
            print(f"处理评论图片时出错: {str(e)}")
            return ''
    # 获取评论视频
    def get_review_video(self, review):
        try:
            videos = review.find_all('input',{'class':'video-url'}) if review.find('input',{'class':'video-url'}) else None
            video_urls = []
            if videos:
                for video in videos:
                    video_url = video.get('value')
                    video_urls.append(video_url)
            return '; '.join(video_urls)
        except Exception as e:
            print(f"处理评论视频时出错: {str(e)}")
            return ''
    # 获取评论内容
    def get_review_content(self, review):
        try:
            review_body = review.find('span', {'data-hook': 'review-body'})
            if review_body:
                for br in review_body.find_all('br'):
                    br.replace_with('\n')
                review_text = review_body.get_text(strip=False)
                review_text = '\n'.join(line for line in review_text.splitlines() if line.strip())
                if review_text:
                    #去除review_text中的"The media could not be loaded." 和第一行的空格
                    review_text = re.sub(r'The media could not be loaded\.', '', review_text)
                    review_text = re.sub(r'^[\s\n]+', '', review_text)
                    return review_text
            return ''
        except Exception as e:
            print(f"处理评论内容时出错: {str(e)}")
            return ''
        
    # 获取评论标题
    def get_review_title(self, review):
        try:
            title_element = review.find('a', {'data-hook': 'review-title'})
            if title_element:
                # 尝试获取最后一个 span 元素的文本
                spans = title_element.find_all('span')
                if spans:
                    # 遍历所有 span，找到包含实际标题的那个
                    for span in spans:
                        # 跳过 "X.X out of 5 stars" 和空格
                        if "stars" not in span.get_text(strip=True) and span.get_text(strip=True):
                            return span.get_text(strip=True)
            else:
                return ''
        except Exception as e:
            print(f"处理评论标题时出错: {str(e)}")
            return ''
    # 获取评论产品的颜色和尺寸
    def get_review_color_size(self, review):
        try:
            format_strip = review.find('div', {'class': 'review-format-strip'})
            if format_strip and format_strip.find('a', {'data-hook':'format-strip'}):
                format_text = format_strip.find('a', {'data-hook':'format-strip'}).get_text(strip=True)
                color = format_text.split('Color:')[-1].split('Size:')[0].strip() if 'Color:' in format_text else ''
                size = format_text.split('Size:')[-1].split('Color:')[0].strip() if 'Size:' in format_text else ''
                return color, size
            else:
                return '', ''
        except Exception as e:
            print(f"处理评论颜色和尺寸时出错: {str(e)}")
            return '', ''
    # 获取评论评分
    def get_review_rating(self, review):
        try:
            rating_element = review.find('i', {'data-hook': 'review-star-rating'})
            rating = rating_element.text.split('.')[0] if rating_element else ''
            return rating
        except Exception as e:
            print(f"处理评论评分时出错: {str(e)}")
            return ''
        
    # 获取评论是否被验证购买
    def get_review_verified(self, review):
        try:
            verified = review.find('span', {'data-hook': 'avp-badge'})
            is_verified = verified.text.strip() if verified else ''
            return is_verified
        except Exception as e:
            print(f"处理评论是否被验证购买时出错: {str(e)}")
            return ''
        
    # 获取评论格式化日期
    def get_review_format_date(self, review):
        try:
            date_span = review.find('span', {'data-hook': 'review-date'})
            formatted_date = self.parse_review_date(date_span.text.strip()) if date_span else ''
            return formatted_date
        except Exception as e:
            print(f"处理评论格式化日期时出错: {str(e)}")
            return ''
        
    # 获取评论所有数据
    def get_reviews(self, asin, pages=10, url_params=None):
        reviews_data = []
        base_url = f'https://www.amazon.com/product-reviews/{asin}'

        # 使用传入的URL参数或默认参数
        default_params = {
            'ie': 'UTF8',
            'reviewerType': 'all_reviews'
        }
        
        if url_params:
            default_params.update(url_params)

        for page in range(1, pages + 1):
            # 更新页码
            default_params['pageNumber'] = str(page)
            
            # 构建查询字符串
            query_string = '&'.join([f'{k}={v}' for k, v in default_params.items()])
            
            # 第一页使用prev，其他页面使用next
            page_type = 'prev' if page == 1 else 'next'
            url = f'{base_url}/ref=cm_cr_getr_d_paging_btm_{page_type}_{page}?{query_string}'
            print(url)
            self.driver.get(url)

            # 模拟滚动一段时间，让页面加载评论
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3,5))

            try:
                # 等待数据加载
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="review"]'))
                )
            except:
                print(f"第 {page} 页未检测到评论元素，可能需要检查是否被要求登录或反爬验证。")
                continue

            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            reviews = soup.select('[data-hook="review"]')

            if reviews:
                print(f"第 {page} 页找到 {len(reviews)} 条评论")
                for review in reviews:
                    try:
                        user_info = self.get_user_info(review)
                        color, size = self.get_review_color_size(review)

                        review_data = {
                            '用户名': user_info['username'],
                            '用户头像': user_info['avatar_url'],
                            '评分': self.get_review_rating(review),
                            '标题': self.get_review_title(review),
                            '评论内容': self.get_review_content(review),
                            '评论时间': self.get_review_format_date(review),
                            '颜色': color,
                            '尺寸': size,
                            '已验证购买': self.get_review_verified(review),
                            '评论图片': self.get_review_images(review),
                            '评论视频': self.get_review_video(review)
                        }
                        reviews_data.append(review_data)
                    except Exception as e:
                        print(f"处理单条评论时出错: {str(e)}")
                        continue
            else:
                print(f"第 {page} 页没有找到评论列表")
            
            time.sleep(random.uniform(2,4))
        return reviews_data
    
    # 保存数据到Excel
    def save_to_excel(self, reviews_data, output_file='amazon_reviews.xlsx'):
        # df_data = []
        # for review in reviews_data:
        #     review_copy = review.copy()
        #     review_copy['缩略图'] = '; '.join(review['评论图片']['缩略图'])
        #     review_copy['原图'] = '; '.join(review['评论图片']['原图'])
        #     del review_copy['评论图片']
        #     df_data.append(review_copy)
            
        df = pd.DataFrame(reviews_data)
        df.to_excel(output_file, index=False)
        print(f"评论已保存到 {output_file}")

def main():
    # 首次运行请将headless=False，在窗口中手动登录Amazon账号后退出，然后再次运行即可。
    scraper = AmazonReviewScraper(headless=False)
    try:
        product_id = 'B07XNZHZ58'  # 替换为你的产品ID
        pages = 1  # 要爬取的页数
        print("开始使用Selenium爬取评论...请在弹出的浏览器窗口中手动登录Amazon账号。")
        reviews = scraper.get_reviews(product_id, pages)
        print(f"总共爬取到 {len(reviews)} 条评论")

        if reviews:
            output_file = f'amazon_reviews_{product_id}.xlsx'
            scraper.save_to_excel(reviews, output_file)
        else:
            print("未找到评论或爬取失败")
            
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
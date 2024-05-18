import requests
import json
import time
import random
from datetime import datetime

def get_json_data(url, headers):
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

def get_video_aid(bv_number):
    aid_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_number}"
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    data = requests.get(aid_url, headers=head).json()
    if data['code'] == 0:
        return data['data']['aid']
    else:
        return None

def generate_url(oid, page):
    base_url = "https://api.bilibili.com/x/v2/reply"
    params = {
        "jsonp": "jsonp",
        "pn": page,
        "type": 1,
        "oid": oid,
        "sort": 2
    }
    url = base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return url

def main():
    bv_number = input("请输入视频的BV号: ")
    num_pages = int(input("请输入要爬取的评论页数: "))
    
    oid = get_video_aid(bv_number)
    if oid:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        
        all_comments = []
        
        print("开始爬取...")
        for page in range(1, num_pages + 1):
            url = generate_url(oid, page)
            json_data = get_json_data(url, headers)
            
            if json_data['code'] == 0:
                replies = json_data['data']['replies']
                if not replies:
                    print(f"第 {page} 页没有评论数据,提前退出爬取")
                    print(f"当前进度: {num_pages}/{num_pages}")
                    break
                
                for reply in replies:
                    comment_info = {
                        'comment': reply['content']['message'],
                        'user_name': reply['member']['uname'],
                        'user_sex': reply['member']['sex'],
                        'like_count': reply['like'],
                        'reply_count': reply['rcount'],
                        'comment_date': datetime.fromtimestamp(reply['ctime']).strftime('%Y-%m-%d %H:%M:%S')  # 添加评论日期
                    }
                    all_comments.append(comment_info)
            else:
                print(f"请求失败,错误码: {json_data['code']}, 错误信息: {json_data['message']}")
            
            # 显示当前进度
            print(f"当前进度: {page}/{num_pages}")
            
            # 随机等待1到3秒
            time.sleep(random.randint(1, 3))
        
        print("整合爬取后的数据...")
        # 按照点赞数递减排序
        sorted_comments = sorted(all_comments, key=lambda x: x['like_count'], reverse=True)
        
        # 将排序后的评论数据保存到文件
        with open(f"{bv_number}_comments.txt", 'w', encoding='utf-8') as file:
            json.dump(sorted_comments, file, ensure_ascii=False, indent=4)
        
        print(f"爬取完成,共爬取{len(all_comments)}条评论,已按点赞数递减排序并保存到{bv_number}_comments.txt文件中。")
    else:
        print("无法获取视频aid")

if __name__ == "__main__":
    main()
# Copyright 2022 The Ip2Region Authors. All rights reserved.
# Use of this source code is governed by a Apache2.0-style
# license that can be found in the LICENSE file.
#
import os,time
from .xdbSearcher import XdbSearcher
import socket
import re
from urllib.parse import urlparse

# 获取脚本所在的文件夹路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取脚本的父目录路径（父路径）
parent_dir = os.path.dirname(script_dir)
print("脚本的父目录路径（父路径）:", parent_dir)

# 获取脚本的父目录的父目录路径（爷路径）
grandparent_dir = os.path.dirname(parent_dir)
print("脚本的父目录的父目录路径（爷路径）:", grandparent_dir)

# 拼接爷路径中的 'data/ip2region.xdb' 文件路径
xdb = os.path.join(grandparent_dir, 'data', 'ip2region.xdb')
print("拼接后的文件路径:", xdb)


# 全局变量，存储加载的 xdb 内容
xdb_content = None

# 初始化 Ip2Region 对象
searcher = None

# 加载 xdb 文件内容
def load_xdb_file():
    global searcher, xdb_content
    if xdb_content is None or searcher is None:  # 添加判断避免重复加载
        print("正在初始化IP数据库...")
        try:
            # 获取当前脚本所在目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建到数据库文件的绝对路径
            db_path = os.path.join(current_dir, '..', '..', 'data', 'ip2region.xdb')
            
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"IP数据库文件未找到: {db_path}")
            
            xdb_content = XdbSearcher.loadContentFromFile(dbfile=db_path)
            searcher = XdbSearcher(contentBuff=xdb_content)
            print("IP数据库加载成功")
        except Exception as e:
            print(f"加载IP数据库失败: {str(e)}")
            raise
    return searcher  # 返回初始化后的searcher对象


# 提取域名或 IP
def extract_domain_or_ip(url):
    # 使用 urlparse 解析 URL
    parsed_url = urlparse(url)
    print('parsed_url---------',parsed_url)
    # 提取域名或 IP 地址部分
    domain_or_ip = parsed_url.hostname
    print('domain_or_ip-------------',domain_or_ip)
    return domain_or_ip

# 判断链接类型：域名或 IP
def is_ip_address(address):
    # 正则表达式匹配 IP 地址
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    return bool(ip_pattern.match(address))

# 获取 IP 地址（如果输入是域名）
def get_ip_from_domain(domain_or_ip):
    if is_ip_address(domain_or_ip):
        return domain_or_ip
    else:
        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                ip_address = socket.gethostbyname(domain_or_ip)
                print(f"Resolved IP: {ip_address}")
                return ip_address
            except socket.gaierror as e:
                print(f"Failed to resolve {domain_or_ip}: {e}")
                retries += 1
                time.sleep(1)  # 等待1秒后重试
        print(f"Failed to resolve {domain_or_ip} after {max_retries} attempts.")
        return None

def searchWithFile():
    # 1. 创建查询对象
    dbPath = xdb
    searcher = XdbSearcher(dbfile=dbPath)
    
    # 2. 执行查询
    ip = "1.2.3.4"
    region_str = searcher.searchByIPStr(ip)
    print(region_str)
    
    # 3. 关闭searcher
    searcher.close()

def searchWithVectorIndex():
     # 1. 预先加载整个 xdb
    dbPath = xdb
    vi = XdbSearcher.loadVectorIndexFromFile(dbfile=dbPath)

    # 2. 使用上面的缓存创建查询对象, 同时也要加载 xdb 文件
    searcher = XdbSearcher(dbfile=dbPath, vectorIndex=vi)
    
    # 3. 执行查询
    ip = "1.2.3.4"
    region_str = searcher.search(ip)
    print(region_str)

    # 4. 关闭searcher
    searcher.close()
    
def searchWithContent(m3u_link):
    domain_or_ip = extract_domain_or_ip(m3u_link)
    print('domain_or_ip----------', domain_or_ip)
    
    # 新增IP格式判断逻辑 ↓
    if is_ip_address(domain_or_ip):  # 使用已存在的判断函数
        ip = domain_or_ip
        print('输入本身就是IP地址:', ip)
    else:
        # 保留原有域名解析逻辑
        ip = get_ip_from_domain(domain_or_ip)
        print('Resolved IP:', ip)
    
    # 如果无法解析 IP 地址，提示用户并跳过后续处理
    if ip is None:
        print(f"无法解析域名 {domain_or_ip} 为 IP 地址。")
        print("可能的原因包括：")
        print("1. 域名无效或不存在，请检查链接的合法性。")
        print("2. 网络连接问题，无法访问外部 DNS 服务器。")
        print("3. 如果不需要解析此链接，可以忽略此错误。")
        return "未知线路"
    
    # 如果 IP 地址有效，继续查询归属地
    if searcher is None:
        raise ValueError("XdbSearcher has not been initialized. Call load_xdb_file first.")
    
    region_str = searcher.search(ip)
    parts = region_str.split('|')
    if len(parts) >= 5:
        country = parts[0]  # 国家
        province = parts[2]  # 省
        city = parts[3]  # 市
        isp = parts[4]       # 运营商
        if isp == '0' or city == '0' or province == '0':
            print(country)
            return country
        else:
            print(city + isp)
            return city + isp
    else:
        print("未知线路")
        return "未知线路"


    
    
if __name__ == '__main__':
    #调用前加载一次数据库
    load_xdb_file()
    searchWithContent('https://txmov2.a.kwimgs.com/bs3/video-hls/5222205336887088723_hlshd15.m3u8')
    #结束后关闭searcher
    searcher.close()
from bs4 import BeautifulSoup
import re









def extract_title(html_content):
    """
    从 HTML 内容中提取文章标题。

    参数:
    - html_content (str): 包含 HTML 的字符串。

    返回:
    - title (str): 提取到的标题文本。如果未找到标题，则返回空字符串。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 先找到类名为 wx-tit 的 div，然后找到其中的第一个 <h1> 标签
    title_tag = soup.select_one('.wx-tit h1')
    if title_tag:
        # 删除 <span> 标签，确保不包含其内容
        span_tag = title_tag.find('span')
        if span_tag:
            span_tag.decompose()  # 移除 <span> 标签
        
        # 获取处理后的标题文本
        return title_tag.get_text(strip=True)



def extract_authors_and_affiliations(html_content):
    """
    从 HTML 内容中分别提取作者姓名和作者所属机构。

    参数:
    - html_content (str): 包含 HTML 的字符串。

    返回:
    - authors (list): 提取到的作者名称列表。
    - affiliations (list): 提取到的作者所属机构列表。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取第一个 h3 标签下的作者姓名
    author_tags = soup.select('.wx-tit h3.author:first-of-type a')
    authors = [author.get_text(strip=True) for author in author_tags]
    
    
    # 提取第二个 h3 标签下的作者机构
    affiliation_tags = soup.select('.wx-tit h3.author:nth-of-type(2) a')
    affiliations = [affiliation.get_text(strip=True) for affiliation in affiliation_tags]
    
    
    return authors, affiliations


def generate_author_affiliations(authors, affiliations_str):
    # 将 affiliation 拆分为字典，键为序号，值为机构名称
    affiliation_dict = {}
    for item in affiliations_str.split(";"):
        item = item.strip()  # 去除前后空格
        match = re.match(r'(\d+)\.(.*)', item)
        if match:
            affiliation_dict[match.group(1)] = match.group(2).strip()
    
    # 初始化一个列表用于存储作者及其机构信息
    author_affiliations = []

    # 解析 author 字段中的作者名和机构序号
    for author in authors:
        name_match = re.match(r'([^\d]+)', author)  # 提取名字（非数字部分）
        if name_match:
            institution_numbers = re.findall(r'\d+', author)        # 提取所有数字部分
            name = name_match.group(0) if name_match else ""
            # 获取该作者的所有机构名称
            institutions = [affiliation_dict[num] for num in institution_numbers if num in affiliation_dict]
            
            # 将作者名和机构名称组合成一个字符串
            if not institutions:
                institutions = affiliations_str
                author_affiliations.append(f"{name} ({''.join(affiliations_str)})")
            else:
                author_affiliations.append(f"{name} ({'; '.join(institutions)})")
            
            
    
    # 返回组合后的字符串
    return "; ".join(author_affiliations)











# 第二阶段，匹配字符 
def extract_all_sibling_divs(html_content, target_div_class):
    """
    从指定的 div 中提取所有同级 div 的内容。

    参数:
    - html_content (str): 包含 HTML 的字符串。
    - target_div_class (str): 目标 div 的类名，用于定位目标 div。

    返回:
    - sibling_divs (list): 包含所有同级 div 文本内容的列表。
    """
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到目标 div
    target_div = soup.find('div', class_=target_div_class)
    
    # 提取目标 div 的所有同级 div
    sibling_divs = []
    if target_div:
        # 查找之前的同级 div
        previous_siblings = target_div.find_previous_siblings('div')
        # 查找之后的同级 div
        next_siblings = target_div.find_next_siblings('div')
        
        # 合并之前和之后的同级 div
        sibling_divs = previous_siblings[::-1] + next_siblings  # 将之前的顺序反转以符合自然顺序
    
    # 返回每个同级 div 的文本内容
    return sibling_divs



def extract_text(div_content, save_dict):
    """
    从 HTML 内容中提取“关键词”标题和对应的关键词内容。

    参数:
    - html_content (str): 包含 HTML 的字符串。

    返回:
    - keywords_title (str): 提取到的“关键词”标题。
    - keywords_content (list): 提取到的关键词列表。
    """
    content = ""    
    other_type_content = ""     # 为什么需要这个？因为这个是累加的
    # 检查 div_content 是否为有效字符串
    if not div_content or not isinstance(div_content, str):
        print("无效的 div_content:", div_content)
        return None, None  # 返回 None 表示无效内容


    
    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(div_content, 'html.parser')
    
    # 提取标题
    name_tags = soup.find_all('span', class_='rowtit')
    for name_tag in name_tags:
        name = name_tag.get_text(strip=True) if name_tag else ""
        if(name == "摘要："):
            content_tag = soup.find('span', class_="abstract-text")
            content = content_tag.get_text(strip=True) if content_tag else None
            save_dict[name] = content
        elif(name == "关键词：" or name == "基金资助："):
            content_tags = soup.find_all('a')
            #content = [content.get_text(strip=True) for content in content_tags]
            content = ' '.join(content.get_text(strip=True) for content in content_tags)
            save_dict[name] = content
        elif(name == "专辑：" or name == "专题：" or name == "分类号："):
            content_tag = name_tag.find_next_sibling('p')
            content = content_tag.get_text(strip=True) if content_tag else None
            save_dict[name] = content  
        else:
            save_dict["其它："] = save_dict["其它："] + soup.get_text(separator=" ", strip=True) + "\n"
    














# 第三阶段，找访问频率
def extract_download_data(html_content, save_dict):

    soup = BeautifulSoup(html_content, 'html.parser')
    div_tag = soup.find("div", class_="opts-down")
    
    # 检查是否找到目标 div
    if div_tag:
        spans = div_tag.find_all("span")
        # 创建键值映射
        data_keys = ["下载：", "页码：", "页数：", "大小："]
        
        # 逐个提取 span 内容并匹配到 save_dict 的对应键
        for i, span in enumerate(spans):
            if i < len(data_keys):  # 确保索引不会超出 data_keys 的长度
                # 提取内容并在值的两侧加上单引号
                key_and_value = span.get_text(strip=True).split("：")
                key = key_and_value[0] + "："
                value = key_and_value[1]
                # 这里不该用序号，应该用字符
                save_dict[key] = value     
        
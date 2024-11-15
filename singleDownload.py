import getInfo
import save
from collections import OrderedDict







html_content = ""
# 使用字典推导式生成有序字典
fieldnames = ["标题：", "作者：", "机构：", "作者及所属机构：", "摘要：", "关键词：", "基金资助：","专题：",  "专辑：", "分类号：", "其它：", "下载：", "页码：","页数：","大小：", "原文url："]








def scrapy_and_save(html_content, url):
    save_dict = OrderedDict((field, "") for field in fieldnames)
    save_dict["原文url："] = url
    # 1、拿到title和作者
    title =  getInfo.extract_title(html_content)
    save_dict["标题："] = title

    authors, affiliations = getInfo.extract_authors_and_affiliations(html_content)
    authors_str = '; '.join(authors)  # 将作者列表转换为分号分隔的字符串
    affiliations_str = '; '.join(affiliations)


    authors_and_affiliations = getInfo.generate_author_affiliations(authors, affiliations_str)
    
    save_dict["作者："] = authors_str
    save_dict["机构："] = affiliations_str
    save_dict["作者及所属机构："] = authors_and_affiliations


    # 2、提取并打印所有同级 div 内容
    sibling_divs = getInfo.extract_all_sibling_divs(html_content, "brief")
    for div_content in sibling_divs:
        style = div_content.get('style', '')
        # 只提取能看得见的字符
        if 'display:none' not in style.replace(" ", ""):  # 去掉空格，确保匹配
            getInfo.extract_text(str(div_content), save_dict)   #必须转为str，否则会报错


    # 3、获取下载量等数据
    getInfo.extract_download_data(html_content, save_dict)
    return save_dict


    




import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse
import sys
import locale

# ====================== 你只需要改这里：QQ邮箱授权码 ======================
EMAIL_USER = "1418085836@qq.com"
EMAIL_PASS = "izuufgefmnevidia"

# ====================== 关键词组A（你给的全部区域/机构）======================
KEYWORDS_GROUP_A = [
    "非洲", "Africa",
    "撒哈拉以南非洲", "Sub-Saharan Africa",
    "北非", "North Africa",
    "南非", "Southern Africa",
    "西非", "West Africa",
    "东非", "East Africa",
    "南部非洲发展共同体", "SADC",
    "西非国家经济共同体", "ECOWAS",
    "非洲大陆自由贸易区", "AfCFTA",
    "中亚", "Central Asia",
    "埃及", "Egypt",
    "利比亚", "Libya",
    "毛里塔尼亚", "Mauritania",
    "塞内加尔", "Senegal",
    "科特迪瓦", "Cote d'Ivoire",
    "尼日利亚", "Nigeria",
    "喀麦隆", "Cameroon",
    "刚果民主共和国", "DRC",
    "安哥拉", "Angola",
    "肯尼亚", "Kenya",
    "乌干达", "Uganda",
    "哈萨克斯坦", "Kazakhstan",
    "乌兹别克斯坦", "Uzbekistan",
    "一带一路", "Belt and Road",
    "中非合作论坛", "FOCAC",
    "中国政府优惠贷款", "Concessional Loan",
    "中国进出口银行", "China Exim Bank",
    "国家国际发展合作署", "CIDCA"
]

# ====================== 关键词组B（你给的全部行业）======================
KEYWORDS_GROUP_B = [
    "智慧城市", "Smart City",
    "数字政府", "e-Government",
    "光纤骨干网", "Fiber Backbone",
    "物联网", "IoT",
    "光伏", "Solar PV",
    "太阳能", "Solar Power",
    "电站", "Power Plant",
    "电网", "Power Grid",
    "输变电", "Transmission Line",
    "变电站", "Substation",
    "矿业", "Mining",
    "矿山供电", "Mine Power Supply",
    "源网荷储", "Source-Grid-Load-Storage",
    "铁路", "Railway",
    "港口", "Port",
    "公路", "Highway",
    "机场", "Airport",
    "基础设施", "Infrastructure",
    "公共工程", "Public Works"
]

# ====================== 百度搜索（按时间最新）======================
def search_baidu(keyword):
    try:
        q = urllib.parse.quote(keyword)
        url = f"https://www.baidu.com/s?wd={q}&tn=baidurt&rn=10"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        res = []
        for item in soup.find_all("div", class_="result-op c-container xpath-log new-pmd")[:10]:
            t = item.find("h3")
            if t:
                title = t.get_text(strip=True)
                a = t.find("a")
                if a and "href" in a.attrs:
                    res.append((title, a["href"]))
        return res
    except:
        return []

# ====================== 谷歌搜索（公开网页）======================
def search_google(keyword):
    try:
        q = urllib.parse.quote(keyword)
        url = f"https://www.google.com/search?q={q}&tbs=qdr:y&num=10"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        res = []
        for g in soup.find_all("div", class_="g")[:10]:
            t = g.find("h3")
            a = g.find("a")
            if t and a and "href" in a.attrs:
                title = t.get_text(strip=True)
                link = a["href"]
                if link.startswith("http"):
                    res.append((title, link))
        return res
    except:
        return []

# ====================== 交叉搜索 + 去重 ======================
def run_all():
    seen = set()
    lines = []
    lines.append(f"【非洲+基建 每日自动搜索】{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("搜索来源：百度 + 谷歌（公开网页，按最新排序）")
    lines.append("=" * 70)

    for a in KEYWORDS_GROUP_A:
        for b in KEYWORDS_GROUP_B:
            kw = f"{a} {b}"
            lines.append(f"\n【关键词】{kw}")

            # 百度
            bd = search_baidu(kw)
            if bd:
                lines.append("→ 百度结果：")
                for t, l in bd:
                    if (t, l) not in seen:
                        seen.add((t, l))
                        lines.append(f"· {t}")
                        lines.append(f"  {l}")

            # 谷歌
            gg = search_google(kw)
            if gg:
                lines.append("→ 谷歌结果：")
                for t, l in gg:
                    if (t, l) not in seen:
                        seen.add((t, l))
                        lines.append(f"· {t}")
                        lines.append(f"  {l}")

            time.sleep(1)

    lines.append("\n" + "="*70)
    lines.append(f"✅ 去重后总计有效信息：{len(seen)} 条")
    return "\n".join(lines)

# ====================== 发邮件（统一1418085836@qq.com）======================
def send_mail(content):
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = Header("非洲基建搜索机器人 <1418085836@qq.com>", "utf-8")
    msg["To"] = Header("1418085836@qq.com", "utf-8")
    msg["Subject"] = Header(f"非洲基建每日情报 {datetime.now().strftime('%Y-%m-%d')}", "utf-8")

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print("邮件失败：", e)

# ====================== 运行 ======================
if __name__ == "__main__":
    content = run_all()
    send_mail(content)

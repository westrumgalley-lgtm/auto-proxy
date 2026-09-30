import base64
import os
import re
import urllib.request

# 这里配置公开节点聚合源（可以根据需要添加更多公开订阅源）
SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/mfuu/v2ray/master/clash.yaml",
]

def fetch_nodes():
    nodes = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in SOURCES:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8", errors="ignore").strip()
                
                # 尝试 Base64 解密
                try:
                    padded = content + "=" * (-len(content) % 4)
                    decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
                    lines = decoded.splitlines()
                except Exception:
                    lines = content.splitlines()
                
                # 提取常见协议节点
                for line in lines:
                    line = line.strip()
                    if re.match(r"^(vmess|vless|ss|ssr|trojan|hysteria2?):\/\/", line, re.I):
                        nodes.append(line)
        except Exception as e:
            print(f"Fetch failed for {url}: {e}")
            
    # 去重
    unique_nodes = list(set(nodes))
    print(f"Total valid nodes fetched: {len(unique_nodes)}")
    return unique_nodes

def export_subscription(nodes):
    os.makedirs("dist", exist_ok=True)
    content = "\n".join(nodes)
    b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # 写入 dist/sub.txt
    with open("dist/sub.txt", "w", encoding="utf-8") as f:
        f.write(b64_content)
    print("Subscription exported successfully to dist/sub.txt")

if __name__ == "__main__":
    node_list = fetch_nodes()
    export_subscription(node_list)
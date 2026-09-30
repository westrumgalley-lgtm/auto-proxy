import base64
import json
import os
import re
import urllib.parse
import urllib.request
import yaml

SOURCES = [
    "https://raw.githubusercontent.com/aiboxeu/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vmess.txt",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yaml",
]

def fetch_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_vmess(link):
    try:
        b64_data = link[8:]
        padded = b64_data + "=" * (-len(b64_data) % 4)
        info = json.loads(base64.b64decode(padded).decode("utf-8", errors="ignore"))
        name = info.get("ps", "vmess-node").strip()
        return {
            "name": name,
            "type": "vmess",
            "server": info.get("add"),
            "port": int(info.get("port")),
            "uuid": info.get("id"),
            "alterId": int(info.get("aid", 0)),
            "cipher": "auto",
            "network": info.get("net", "tcp"),
            "tls": info.get("tls") == "tls",
        }
    except Exception:
        return None

def main():
    os.makedirs("dist", exist_ok=True)
    proxies = []
    seen_names = set()

    for url in SOURCES:
        text = fetch_content(url)
        if not text:
            continue

        try:
            data = yaml.safe_load(text)
            if isinstance(data, dict) and "proxies" in data:
                for p in data["proxies"]:
                    if isinstance(p, dict) and p.get("name") and p["name"] not in seen_names:
                        seen_names.add(p["name"])
                        proxies.append(p)
                continue
        except Exception:
            pass

        try:
            padded = text.strip() + "=" * (-len(text.strip()) % 4)
            decoded = base64.b64decode(padded).decode("utf-8", errors="ignore")
            lines = decoded.splitlines()
        except Exception:
            lines = text.splitlines()

        for line in lines:
            line = line.strip()
            if line.startswith("vmess://"):
                node = parse_vmess(line)
                if node and node["name"] not in seen_names:
                    seen_names.add(node["name"])
                    proxies.append(node)

    proxy_names = [p["name"] for p in proxies] if proxies else ["DIRECT"]

    clash_config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "external-controller": "127.0.0.1:9090",
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": "节点选择",
                "type": "select",
                "proxies": proxy_names
            },
            {
                "name": "自动选择",
                "type": "url-test",
                "proxies": proxy_names,
                "url": "http://www.gstatic.com/generate_204",
                "interval": 300
            }
        ],
        "rules": [
            "GEOIP,CN,DIRECT",
            "MATCH,节点选择"
        ]
    }

    output_path = os.path.join("dist", "config.yaml")
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)
    print(f"Clash config generated: {len(proxies)} proxies")

if __name__ == "__main__":
    main()

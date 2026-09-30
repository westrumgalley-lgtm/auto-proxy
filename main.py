import os
import urllib.request
import yaml

# 优质公开 clash 节点订阅源
SOURCES = [
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    "https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/clash.yaml",
    "https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list.yml"
]

def fetch_data(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ClashforWindows/0.20.39"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Fetch failed for {url}: {e}")
        return ""

def main():
    os.makedirs("dist", exist_ok=True)
    all_proxies = []
    seen = set()

    for url in SOURCES:
        content = fetch_data(url)
        if not content:
            continue
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict) and "proxies" in data and isinstance(data["proxies"], list):
                for p in data["proxies"]:
                    if isinstance(p, dict) and p.get("name") and p["name"] not in seen:
                        seen.add(p["name"])
                        all_proxies.append(p)
        except Exception as e:
            print(f"Parse error for {url}: {e}")

    print(f"Total valid proxies collected: {len(all_proxies)}")

    proxy_names = [p["name"] for p in all_proxies] if all_proxies else ["DIRECT"]

    clash_config = {
        "port": 7890,
        "socks-port": 7891,
        "allow-lan": False,
        "mode": "rule",
        "log-level": "info",
        "proxies": all_proxies,
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

    with open("dist/config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(clash_config, f, allow_unicode=True, sort_keys=False)

if __name__ == "__main__":
    main()

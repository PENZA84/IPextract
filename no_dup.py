import base64
import json
import re
from urllib.parse import urlparse, parse_qs, unquote

def parse_vless(config):
    parts = config.split("://")[1].split("#")
    main_part = parts[0]
    remark = unquote(parts[1]) if len(parts) > 1 else ""
    uuid_and_address, params = main_part.split("?")
    uuid, rest = uuid_and_address.split("@")
    url = urlparse(f"https://{rest}?{params}")
    query = parse_qs(url.query)
    return {
        'address': url.hostname,
        'port': url.port,
        'uuid': uuid,
        'sni': query.get('sni', [None])[0],
        'path': query.get('path', [None])[0],
        'remark': remark
    }

def parse_ss(config):
    try:
        parts = config.split("://")[1].split("#")
        main_part = parts[0]
        remark = unquote(parts[1]) if len(parts) > 1 else ""
        user_info, rest = main_part.split("@")
        encoded = user_info
        encoded += "=" * ((4 - len(encoded) % 4) % 4)
        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
        method, password = decoded.split(':')
        url = urlparse(f"https://{rest}")
        return {
            'address': url.hostname,
            'port': url.port,
            'password': password,
            'encryption': method,
            'remark': remark
        }
    except Exception as e:
        print(f"Error parsing SS config: {config}")
        print(f"Error details: {str(e)}")
        return None

def parse_hysteria2(config):
    parts = config.split("://")[1].split("#")
    main_part = parts[0]
    remark = unquote(parts[1]) if len(parts) > 1 else ""
    password, rest = main_part.split("@")
    url = urlparse(f"https://{rest}")
    query = parse_qs(url.query)
    return {
        'address': url.hostname,
        'port': url.port,
        'password': password,
        'sni': query.get('sni', [None])[0],
        'remark': remark
    }

def parse_trojan(config):
    parts = config.split("://")[1].split("#")
    main_part = parts[0]
    remark = unquote(parts[1]) if len(parts) > 1 else ""
    password, rest = main_part.split("@")
    url = urlparse(f"https://{rest}")
    query = parse_qs(url.query)
    return {
        'address': url.hostname,
        'port': url.port,
        'password': password,
        'sni': query.get('sni', [None])[0],
        'path': query.get('path', [None])[0],
        'remark': remark
    }

def parse_vmess(config):
    try:
        encoded = config.split("://")[1]
        encoded += "=" * ((4 - len(encoded) % 4) % 4)
        decoded = base64.urlsafe_b64decode(encoded).decode('utf-8')
        data = json.loads(decoded)
        return {
            'address': data['add'],
            'port': data['port'],
            'uuid': data['id'],
            'sni': data.get('sni'),
            'path': data.get('path'),
            'remark': data.get('ps', '')
        }
    except Exception as e:
        print(f"Error parsing VMess config: {config}")
        print(f"Error details: {str(e)}")
        return None

def remove_duplicates(configs):
    unique_configs = []
    seen = set()

    for config in configs:
        try:
            if config.startswith("vless://"):
                parsed = parse_vless(config)
                key = f"vless:{parsed['address']}:{parsed['port']}:{parsed['uuid']}:{parsed['sni']}:{parsed['path']}"
            elif config.startswith("ss://"):
                parsed = parse_ss(config)
                if parsed is None:
                    continue
                key = f"ss:{parsed['address']}:{parsed['port']}:{parsed['password']}:{parsed['encryption']}"
            elif config.startswith(("hysteria2://", "hy2://")):
                parsed = parse_hysteria2(config)
                key = f"hy2:{parsed['address']}:{parsed['port']}:{parsed['password']}:{parsed['sni']}"
            elif config.startswith("trojan://"):
                parsed = parse_trojan(config)
                key = f"trojan:{parsed['address']}:{parsed['port']}:{parsed['password']}:{parsed['sni']}:{parsed['path']}"
            elif config.startswith("vmess://"):
                parsed = parse_vmess(config)
                if parsed is None:
                    continue
                key = f"vmess:{parsed['address']}:{parsed['port']}:{parsed['uuid']}:{parsed['sni']}:{parsed['path']}"
            else:
                # Unknown config type, keep it
                unique_configs.append(config)
                continue

            if key not in seen:
                seen.add(key)
                unique_configs.append(config)
        except Exception as e:
            print(f"Error processing config: {config}")
            print(f"Error details: {str(e)}")
            continue

    return unique_configs

def main():
    try:
        with open('proxies.txt', 'r', encoding='utf-8') as f:
            configs = f.read().splitlines()
    except UnicodeDecodeError:
        print("Error: Unable to read the file with UTF-8 encoding. Trying with 'iso-8859-1' encoding...")
        try:
            with open('proxies.txt', 'r', encoding='iso-8859-1') as f:
                configs = f.read().splitlines()
        except Exception as e:
            print(f"Error: Unable to read the file. {str(e)}")
            return

    unique_configs = remove_duplicates(configs)

    try:
        with open('nodup_proxies.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(unique_configs))
        print("Successfully created nodup_proxies.txt with deduplicated configs.")
    except Exception as e:
        print(f"Error: Unable to write to the output file. {str(e)}")

if __name__ == "__main__":
    main()

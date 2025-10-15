#!/usr/bin/env python3
"""
检查 artifact_url 的可达性
"""
import json
import sys
from pathlib import Path

import requests


def main():
    """主函数"""
    try:
        # 读取变更条目
        changed_entry_path = Path('changed_entry.json')
        changed_entry = json.loads(changed_entry_path.read_text())

        artifact_url = changed_entry.get('artifact_url')
        if not artifact_url:
            print("::error::artifact_url field is missing")
            sys.exit(1)

        print(f"Checking artifact URL: {artifact_url}")

        # 发送 HEAD 请求检查 URL 可达性
        try:
            response = requests.head(artifact_url, allow_redirects=True, timeout=30)

            if response.status_code < 200 or response.status_code >= 300:
                print(f"::error::artifact_url returned status code {response.status_code}")
                print(f"URL: {artifact_url}")
                sys.exit(1)

            # 检查 Content-Type (可选但推荐)
            content_type = response.headers.get('Content-Type', '')
            if 'application/zip' not in content_type and 'application/octet-stream' not in content_type and 'binary' not in content_type:
                print(f"::warning::artifact_url Content-Type is '{content_type}', expected binary/zip format")

            # 检查 Content-Length
            content_length = response.headers.get('Content-Length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f"Artifact size: {size_mb:.2f} MB")

                # 警告过大的文件
                if size_mb > 100:
                    print(f"::warning::Artifact size is {size_mb:.2f} MB, which is quite large")

            print(f"✅ artifact_url is accessible (HTTP {response.status_code})")

        except requests.RequestException as e:
            print(f"::error::Failed to access artifact_url: {e}")
            print(f"URL: {artifact_url}")
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"::error::File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"::error::Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


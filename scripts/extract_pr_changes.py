#!/usr/bin/env python3
"""
提取 PR 中新增或修改的预制件条目
"""
import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> str:
    """运行命令并返回输出"""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def main():
    """主函数"""
    try:
        # 获取 base 和 head 的文件内容
        base_content = run_command([
            'git', 'show', 'origin/main:community-prefabs.json'
        ])
        head_content = run_command([
            'git', 'show', 'HEAD:community-prefabs.json'
        ])

        base_data = json.loads(base_content) if base_content else []
        head_data = json.loads(head_content)

        # 找出新增或修改的条目
        base_set = {(item['id'], item['version']) for item in base_data}
        head_set = {(item['id'], item['version']) for item in head_data}

        new_entries = head_set - base_set

        if not new_entries:
            print("::error::No new prefab entries found in this PR")
            sys.exit(1)

        if len(new_entries) > 1:
            print("::error::Only one prefab entry should be added per PR")
            print(f"Found {len(new_entries)} new entries: {new_entries}")
            sys.exit(1)

        # 提取新条目的完整信息
        new_id, new_version = list(new_entries)[0]
        changed_entry = None

        for item in head_data:
            if item['id'] == new_id and item['version'] == new_version:
                changed_entry = item
                break

        if not changed_entry:
            print("::error::Could not find the changed entry")
            sys.exit(1)

        # 保存到文件供后续步骤使用
        output_path = Path('changed_entry.json')
        output_path.write_text(json.dumps(changed_entry, indent=2, ensure_ascii=False))

        print(f"✅ Extracted changed entry: {new_id}@{new_version}")
        print(f"Entry saved to: {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"::error::Failed to run git command: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"::error::Invalid JSON format: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"::error::Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


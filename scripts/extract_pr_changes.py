#!/usr/bin/env python3
"""
从 PR 中提取修改的 prefab 条目

支持三种类型的变更：
1. 新增 prefab（新的 id）
2. 版本更新（已存在的 id，新的 version）
3. 元数据更新（相同 id+version，不同内容）
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

        # 创建字典方便查找
        base_dict = {(item['id'], item['version']): item for item in base_data}
        head_dict = {(item['id'], item['version']): item for item in head_data}
        base_ids = {item['id'] for item in base_data}

        # 分类不同类型的变更
        new_prefabs = []      # 全新的 prefab（新 id）
        new_versions = []     # 已存在 prefab 的新版本（已存在 id，新 version）
        updated_metadata = [] # 元数据更新（相同 id+version，不同内容）
        deleted_entries = []  # 删除的条目

        # 检查 HEAD 中的条目
        for key, head_item in head_dict.items():
            prefab_id, version = key

            if key not in base_dict:
                # 这个 id+version 组合是新的
                if prefab_id in base_ids:
                    # id 已存在 -> 这是一个新版本
                    new_versions.append(key)
                else:
                    # id 也是新的 -> 这是一个全新的 prefab
                    new_prefabs.append(key)
            elif head_item != base_dict[key]:
                # id+version 存在但内容不同 -> 元数据更新
                updated_metadata.append(key)

        # 检查删除的条目
        for key in base_dict.keys():
            if key not in head_dict:
                deleted_entries.append(key)

        # 计算总变更数
        total_changes = len(new_prefabs) + len(new_versions) + len(updated_metadata) + len(deleted_entries)

        if total_changes == 0:
            print("::error::No changes found in community-prefabs.json")
            print("Each PR should add or update exactly one prefab entry")
            sys.exit(1)

        if deleted_entries:
            print(f"::error::PR contains {len(deleted_entries)} deletion(s), which is not allowed:")
            for key in deleted_entries:
                print(f"  - {key[0]}@{key[1]}")
            sys.exit(1)

        if total_changes > 1:
            print(f"::error::Found {total_changes} change(s), but only 1 is allowed per PR:")
            if new_prefabs:
                print(f"  New prefabs ({len(new_prefabs)}):")
                for key in new_prefabs:
                    print(f"    - {key[0]}@{key[1]}")
            if new_versions:
                print(f"  New versions ({len(new_versions)}):")
                for key in new_versions:
                    print(f"    - {key[0]}@{key[1]}")
            if updated_metadata:
                print(f"  Metadata updates ({len(updated_metadata)}):")
                for key in updated_metadata:
                    print(f"    - {key[0]}@{key[1]}")
            sys.exit(1)

        # 确定变更类型和条目
        if new_prefabs:
            changed_key = new_prefabs[0]
            change_type = "new prefab"
        elif new_versions:
            changed_key = new_versions[0]
            change_type = "new version"
        else:
            changed_key = updated_metadata[0]
            change_type = "metadata update"

        changed_entry = head_dict[changed_key]
        prefab_id, version = changed_key

        # 显示变更信息
        print(f"✅ Found {change_type}: {prefab_id}@{version}")

        if change_type == "new version":
            # 显示之前的版本
            old_versions = [v for (id, v) in base_dict.keys() if id == prefab_id]
            if old_versions:
                print(f"Previous versions: {', '.join(sorted(old_versions))}")

        elif change_type == "metadata update":
            # 显示具体变更的字段
            base_item = base_dict[changed_key]
            changes = []
            for key in changed_entry.keys():
                if changed_entry[key] != base_item.get(key):
                    old_val = json.dumps(base_item.get(key), ensure_ascii=False)
                    new_val = json.dumps(changed_entry[key], ensure_ascii=False)
                    changes.append(f"  - {key}: {old_val} → {new_val}")
            if changes:
                print("Changes detected:")
                print("\n".join(changes))

        # 保存到文件供后续步骤使用
        output_path = Path('changed_entry.json')
        output_path.write_text(json.dumps(changed_entry, indent=2, ensure_ascii=False))

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


# scripts/convert.py
import os

# 配置：数据源目录 (在 CI 环境中，我们会把 v2fly 代码拉取到 upstream 目录)
DATA_DIR = "./upstream/data"
# 配置：需要提取的分类
TARGET_LIST = "cn"
# 配置：输出文件路径
OUTPUT_FILE = "./cn-direct.txt"

def parse_file(filename, seen_domains, seen_files):
    if filename in seen_files: return
    seen_files.add(filename)
    
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        print(f"Warning: File not found {filename}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                
                # 处理引用 include:
                if line.startswith('include:'):
                    parse_file(line.split(':')[1], seen_domains, seen_files)
                    continue

                # 清洗数据，只保留域名
                parts = line.split(':')
                type_tag = parts[0] if len(parts) > 1 else "domain"
                value = parts[1] if len(parts) > 1 else parts[0]
                value = value.split('@')[0] # 去掉属性

                # 【核心】丢弃正则和关键字，只保留纯域名
                if type_tag in ["regexp", "keyword"]:
                    continue
                
                seen_domains.add(value)
    except Exception as e:
        print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    domains = set()
    files_processed = set()
    
    print("Starting conversion...")
    parse_file(TARGET_LIST, domains, files_processed)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 写入头部注释
        f.write(f"# Auto-generated from v2fly/domain-list-community [{TARGET_LIST}] (No Regex)\n")
        for d in sorted(domains):
            f.write(d + "\n")
            
    print(f"Success! Generated {len(domains)} lines to {OUTPUT_FILE}")

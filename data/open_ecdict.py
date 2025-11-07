# -*- coding: utf-8 -*-
import os
import re
import json
import time

# --- 1. 配置区域 ---
# 主词头文件
HW_FILE = 'ODE 词头.txt'

# 数据源文件 (按fallback顺序)
SOURCE_FILES = {
    1: '英语专业四八级词汇表.txt',
    2: '现代英汉词典.txt',
    3: 'OALD8_简体中文释义.txt',
    4: 'oxford_dict_result.txt',
    5: 'extracted_from_ODE.txt'
}

# 输出文件
TXT_OUTPUT_FILE = 'final_vocabulary.txt'
JSON_OUTPUT_FILE = 'final_vocabulary.json'

# 中间索引文件 (用于缓存和检查)
INDEX_FILES = {
    1: 'index_1.json',
    2: 'index_2.json',
    3: 'index_3.json',
    4: 'index_4.json',
    5: 'index_5.json'
}


# --- 2. 辅助函数 ---

def save_index_to_json(data, filename):
    """将字典或列表数据保存为格式化的JSON文件。"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ 数据已成功保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存到 {filename} 时出错: {e}")

def extract_pron_and_def_from_brackets(text):
    """从文本中提取方括号 [...] 内的音标。"""
    pattern = re.compile(r"(\[.*?\])")
    match = pattern.search(text)
    if match:
        pron = match.group(1)
        definition = text.replace(match.group(0), '').strip()
        return pron, definition
    return None, text.strip()


# --- 3. 专用索引构建函数 ---

def build_index_from_file_1(filepath):
    """为源文件1构建索引 (音标格式: [...])。"""
    print(f"--- 正在为 {filepath} 构建索引 ---")
    index = {}
    headword_pattern = re.compile(r"^(\*?[\w\s\.-]+?)\s+(.*)")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                match = headword_pattern.match(line)
                if match:
                    headword = match.group(1).replace('*', '').strip()
                    full_def = match.group(2).strip()
                    pron, definition = extract_pron_and_def_from_brackets(full_def)
                    if headword:
                        if headword in index:
                            index[headword]['def'] += f" | {definition}"
                            if not index[headword]['pron'] and pron:
                                index[headword]['pron'] = pron
                        else:
                            index[headword] = {"pron": pron, "def": definition}
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {filepath}"); return None
    print(f"构建完成，共索引 {len(index)} 个词条。")
    return index

def build_index_from_file_2(filepath):
    """为源文件2构建索引 (音标格式: /.../ -> [...])。"""
    print(f"--- 正在为 {filepath} 构建索引 ---")
    index = {}
    headword_pattern = re.compile(r"^([\w\s'-]+?)\s*((?:/|\s{2,}).*)")
    pron_pattern = re.compile(r"\/(.*?)\/")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                match = headword_pattern.match(line)
                if match:
                    headword, full_def = match.group(1).strip(), match.group(2).strip()
                    pron, definition = None, full_def
                    pron_match = pron_pattern.search(full_def)
                    if pron_match:
                        pron = f"[{pron_match.group(1)}]"
                        definition = full_def.replace(pron_match.group(0), '').strip()
                    if headword:
                        if headword in index:
                            index[headword]['def'] += f" | {definition}"
                            if not index[headword]['pron'] and pron:
                                index[headword]['pron'] = pron
                        else:
                            index[headword] = {"pron": pron, "def": definition}
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {filepath}"); return None
    print(f"构建完成，共索引 {len(index)} 个词条。")
    return index

def build_index_from_file_3(filepath):
    """为源文件3构建索引 (音标格式: [...])。"""
    print(f"--- 正在为 {filepath} 构建索引 ---")
    index = {}
    headword_pattern = re.compile(r"^([\w\s'-]+?)\s*((?:\[|\s{2,}).*)")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                match = headword_pattern.match(line)
                if match:
                    headword, full_def = match.group(1).strip(), match.group(2).strip()
                    pron, definition = extract_pron_and_def_from_brackets(full_def)
                    if headword:
                        if headword in index:
                            index[headword]['def'] += f" | {definition}"
                            if not index[headword]['pron'] and pron:
                                index[headword]['pron'] = pron
                        else:
                            index[headword] = {"pron": pron, "def": definition}
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {filepath}"); return None
    print(f"构建完成，共索引 {len(index)} 个词条。")
    return index

def build_index_from_file_4(filepath):
    """为源文件4构建索引 (音标在独立行)。"""
    print(f"--- 正在为 {filepath} 构建索引 ---")
    index = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f: content = f.read()
        entries = re.split(r'\n\s*\n', content)
        for entry in entries:
            entry = entry.strip()
            if not entry: continue
            lines = [l.strip() for l in entry.split('\n')]
            headword = lines[0]
            pron, definition_lines = None, lines[1:]
            if len(lines) > 1 and lines[1].startswith('/') and lines[1].endswith('/'):
                pron_content = lines[1].strip(' /')
                pron = f"[{pron_content}]"
                definition_lines = lines[2:]
            definition = ' '.join(definition_lines)
            if headword and headword not in index:
                index[headword] = {"pron": pron, "def": definition}
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {filepath}"); return None
    print(f"构建完成，共索引 {len(index)} 个词条。")
    return index

def build_index_from_file_5(filepath):
    """为源文件5构建索引 (音标格式: /.../ -> [...])。"""
    print(f"--- 正在为 {filepath} 构建索引 ---")
    index = {}
    separator = '⇒'
    pron_pattern = re.compile(r"\/(.*?)\/")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or separator not in line: continue
                parts = line.split(separator, 1)
                headword, full_def = parts[0].strip(), parts[1].strip()
                pron, definition = None, full_def
                pron_match = pron_pattern.search(full_def)
                if pron_match:
                    pron = f"[{pron_match.group(1)}]"
                    definition = full_def.replace(pron_match.group(0), '').strip()
                if headword:
                    if headword in index:
                        index[headword]['def'] += f" | {definition}"
                        if not index[headword]['pron'] and pron:
                            index[headword]['pron'] = pron
                    else:
                        index[headword] = {"pron": pron, "def": definition}
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {filepath}"); return None
    print(f"构建完成，共索引 {len(index)} 个词条。")
    return index

# --- 4. 主程序 ---
def main():
    """主程序，协调索引构建、数据合并和文件输出。"""
    total_start_time = time.time()

    # 阶段一: 构建所有数据源的索引
    print("===== 阶段一: 开始构建索引 =====")
    indexes = {}
    tasks = [
        # (1, build_index_from_file_1, SOURCE_FILES[1], INDEX_FILES[1]),
        (2, build_index_from_file_2, SOURCE_FILES[2], INDEX_FILES[2]),
        (3, build_index_from_file_3, SOURCE_FILES[3], INDEX_FILES[3]),
        (4, build_index_from_file_4, SOURCE_FILES[4], INDEX_FILES[4]),
        (5, build_index_from_file_5, SOURCE_FILES[5], INDEX_FILES[5]),
    ]
    for num, build_func, src_file, idx_file in tasks:
        idx = build_func(src_file)
        if idx is not None:
            indexes[num] = idx
            save_index_to_json(idx, idx_file)
    print("===== 索引构建阶段完成 =====\n")

    # 阶段二: 读取主词头列表，并合并数据
    print("===== 阶段二: 开始合并词汇表 =====")
    try:
        with open(HW_FILE, 'r', encoding='utf-8') as f:
            headword_lines = [line.strip() for line in f if line.strip()]
        print(f"从 {HW_FILE} 读取了 {len(headword_lines)} 行。")
    except FileNotFoundError:
        print(f"❌ 致命错误: 词头文件 {HW_FILE} 未找到。程序终止。"); return

    final_data_list = []
    found_count, redirect_count = 0, 0
    with open(TXT_OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        for line in headword_lines:
            # 检查是否为跳转链接
            if '►@@@LINK' in line:
                redirect_count += 1
                f_out.write(f"{line}\n\n")
                parts = line.split('►', 1)
                hw, link_def = parts[0].strip(), '►' + parts[1].strip()
                entry_data = {"headword": hw, "pron": None, "def": link_def, "source": "redirect"}
            else:
                hw, found_entry, source_num = line, None, 0
                # 按顺序在索引中查找
                for i in sorted(indexes.keys()):
                    if indexes.get(i) and hw in indexes[i]:
                        found_entry = indexes[i][hw]
                        source_num = i
                        break
                
                if found_entry:
                    found_count += 1
                    pron_str = found_entry.get('pron') or ''
                    def_str = found_entry.get('def', '')

                    if pron_str:
                        full_def_str = f"{pron_str} ※ {def_str}".strip()
                    else:
                        full_def_str = def_str
                    
                    f_out.write(f"{hw} ⇒ {full_def_str} 〇〈{source_num}〉\n\n")
                    entry_data = {"headword": hw, "pron": found_entry.get('pron'), "def": def_str, "source": source_num}
                else:
                    f_out.write(f"{hw} <Not Found>\n\n")
                    entry_data = {"headword": hw, "pron": None, "def": None, "source": 0}
            
            final_data_list.append(entry_data)
    print("===== 合并阶段完成 =====\n")

    # 阶段三: 输出最终的JSON文件
    print("===== 阶段三: 生成JSON输出文件 =====")
    save_index_to_json(final_data_list, JSON_OUTPUT_FILE)
    print("===== JSON生成阶段完成 =====\n")

    # 最终报告
    total_end_time = time.time()
    total_entries = len(headword_lines)
    not_found_count = total_entries - found_count - redirect_count
    print("===== 处理完成 =====")
    print(f"🎉 全部任务结束！")
    print(f"    - 总处理词头数: {total_entries}")
    print(f"    - 成功匹配释义: {found_count}")
    print(f"    - 跳转链接词条: {redirect_count}")
    print(f"    - 未能匹配词条: {not_found_count}")
    print("-" * 20)
    print(f"    - TXT 词汇表已生成: {TXT_OUTPUT_FILE}")
    print(f"    - JSON 词汇表已生成: {JSON_OUTPUT_FILE}")
    print(f"    - 中间索引文件已生成 (index_*.json)")
    print("-" * 20)
    print(f"    - 总耗时: {total_end_time - total_start_time:.2f} 秒")

if __name__ == '__main__':
    main()
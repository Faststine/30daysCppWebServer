import os

# 定义基础目录
base_dir = '.'
code_dir = os.path.join(base_dir, 'code')

# 获取所有以 day 开头的 md 文件，并按顺序排序
md_files = [f for f in os.listdir(base_dir) if f.startswith('day') and f.endswith('.md')]
md_files.sort()

# 定义合并后的文件路径
merged_file_path = 'merged_days.md'

# 打开合并后的文件以写入内容
with open(merged_file_path, 'w', encoding='utf-8') as merged_file:
    for md_file in md_files:
        print(f"正在处理 {md_file}...")

        # 打开当前的 md 文件以读取内容
        with open(os.path.join(base_dir, md_file), 'r', encoding='utf-8') as current_md_file:
            # 读取当前 md 文件的内容
            content = current_md_file.read()
            # 将当前 md 文件的内容写入合并后的文件
            merged_file.write(content)
        print(f"已合并 {md_file} 的内容。")

        # 获取对应的 day 目录
        # 假设 md 文件名称格式为 dayXX_具体描述.md，code 目录下子目录名称为 dayXX
        day_dir_name = md_file.split('-')[0].replace('.md', '')
        day_dir_path = os.path.join(code_dir, day_dir_name)

        # 检查目录是否存在
        if os.path.isdir(day_dir_path):
            print(f"找到对应的目录 {day_dir_path}。")
            # 查找目录中的 cpp 文件和 makefile 文件
            cpp_files = [f for f in os.listdir(day_dir_path) if f.endswith('.cpp')]
            makefile_files = [f for f in os.listdir(day_dir_path) if f.lower() == 'makefile']

            # 写入 cpp 文件内容
            for cpp_file in cpp_files:
                print(f"正在合并 {cpp_file} 的内容...")
                merged_file.write(f'\n## {cpp_file}\n')
                merged_file.write('```cpp\n')
                with open(os.path.join(day_dir_path, cpp_file), 'r', encoding='utf-8') as cpp_f:
                    merged_file.write(cpp_f.read())
                merged_file.write('\n```\n')
                print(f"已合并 {cpp_file} 的内容。")

            # 写入 makefile 文件内容
            for makefile in makefile_files:
                print(f"正在合并 {makefile} 的内容...")
                merged_file.write(f'\n## {makefile}\n')
                merged_file.write('```makefile\n')
                with open(os.path.join(day_dir_path, makefile), 'r', encoding='utf-8') as make_f:
                    merged_file.write(make_f.read())
                merged_file.write('\n```\n')
                print(f"已合并 {makefile} 的内容。")
        else:
            print(f"未找到对应的目录 {day_dir_path}。")

        # 在每个 day 内容后添加分隔线
        merged_file.write('\n---\n\n')
        print(f"完成 {md_file} 的处理。")

print(f'所有内容已合并到 {merged_file_path} 文件中。')
    
from ruamel.yaml import YAML


def update_yaml_pyyaml(file_path, context):
    """保留注释和格式的YAML修改实现"""
    yaml = YAML()
    yaml.preserve_quotes = True  # 保留字符串引号风格
    yaml.indent(mapping=2, sequence=4, offset=2)  # 保持原始缩进

    # 加载文件（保留注释）
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.load(f)

    # 递归更新字段（逻辑与PyYAML相同）
    def set_nested_key(target_dict, key_list, value):
        current_key = key_list.pop(0)
        if key_list:
            set_nested_key(target_dict.setdefault(current_key, {}), key_list, value)
        else:
            target_dict[current_key] = value

    for key_path, value in context.items():
        keys = key_path.split('.')
        set_nested_key(data, keys.copy(), value)

    # 写回文件（保持原有格式）
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)
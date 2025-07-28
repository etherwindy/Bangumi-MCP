subject_types = {
    1: "书籍",
    2: "动画",
    3: "音乐",
    4: "游戏",
    6: "三次元"
}

person_types = {
    1: "个人",
    2: "公司",
    3: "组合"
}

character_types = {
    1: "角色",
    2: "机体",
    3: "舰船",
    4: "组织"
}

episode_types = {
    0: "本篇",
    1: "SP",
    2: "OP",
    3: "ED",
}

collection_types = {
    1: "想看",
    2: "看过",
    3: "在看",
    4: "搁置",
    5: "抛弃"
}

episode_collection_types = {
    0: "未收藏",
    1: "想看",
    2: "看过",
    3: "抛弃"
}

collection_translations = {
    "wish": "想看",
    "collect": "看过",
    "doing": "在看",
    "on_hold": "搁置",
    "drop": "抛弃"
}

user_group = {
    1: "管理员",
    2: "Bangumi 管理猿",
    3: "天窗管理猿",
    4: "禁言用户",
    5: "禁止访问用户",
    8: "人物管理猿",
    9: "维基条目管理猿",
    10: "用户",
    11: "维基人"
}


def indent_text(text: str, indent: int = 2) -> str:
    """
    Indent the given text with spaces.
    
    Args:
        text: The text to indent.
        indent: Number of spaces to indent.
        
    Returns:
        Indented text.
    """
    return "\n".join(" " * indent + line for line in text.splitlines())


def parse_image_urls(info: dict) -> str:
    """
    Parse image URLs from the given dictionary and format them into a string.
    
    Args:
        images: Dictionary containing image URLs.
        
    Returns:
        Formatted string with image URLs.
    """
    images = info.get('images', None)

    if not images:
        output = ""
    else:
        output =\
            f"- 图片 URL:\n"\
            f"  - 网格: {images.get('grid', 'N/A')}\n"\
            f"  - 小图: {images.get('small', 'N/A')}\n"\
            f"  - 中图: {images.get('medium', 'N/A')}\n"\
            f"  - 常规: {images.get('common', 'N/A')}\n"\
            f"  - 大图: {images.get('large', 'N/A')}\n"
    
    return output


def parse_lagacy_subject_small_info(info: dict) -> str:
    """
    解析旧版条目信息为字符串格式
    """
    
    rating = info.get('rating', {})

    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - URL: {info.get('url', 'N/A')}\n"\
        f"  - 类型: {subject_types.get(info['type'], '未知')}\n"
    if info.get('date'):
        output += f"  - 开播日期: {info['date']}\n"
    if info.get('summary'):
        output += f"  - 简介: {info['summary']}\n"
    output += \
        f"  - 首映日期: {info.get('air_date', 'N/A')}\n"\
        f"  - 放送星期: {info.get('air_weekday', 'N/A')}\n"
    output += indent_text(parse_image_urls(info))
    output += \
        f"  - 评分: {rating.get('score', 'N/A')} ({rating.get('total', 'N/A')}人)\n"\
        f"  - 评分分布:\n"
    for key, value in rating.get('count', {}).items():
        output += f"    - {key}: {value}人\n"
    output += f"  - 排名: {rating.get('rank', 'N/A')}\n"

    return output


def parse_subject_info(info: dict, brief: bool=False) -> str:
    """

    """

    tags = [f"{tag['name']}({tag['count']})" for tag in info['tags']]
    rating = info.get('rating', {})

    if brief:
        summary = info['summary'][:100] + "..." if len(info['summary']) > 100 else info['summary']
        tags = tags[:5]  # Limit tags to 5 for brief output
        collection_total = sum([v for k, v in info.get('collection', {}).items()])
        output = \
            f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
            f"  - 类型: {subject_types.get(info['type'], '未知')}\n"
        if info.get('date'):
            output += f"  - 开播日期: {info['date']}\n"
        output += \
            f"  - 平台: {info['platform']}\n"\
            f"  - 标签: {', '.join(tags)}\n"\
            f"  - 简介: {summary}\n"
        output += indent_text(parse_image_urls(info))
        output += \
            f"  - 评分: {rating.get('score', 'N/A')}, ({rating.get('total', 'N/A')}人)\n"\
            f"  - 排名: {rating.get('rank', 'N/A')}\n"\
            f"  - 收藏总数: {collection_total}\n"
    else       :
        output = \
            f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')} ID: {info.get('id', 'N/A')})\n"\
            f"  - 类型: {subject_types.get(info['type'], '未知')}\n"\
            f"  - NSFW: {'是' if info['nsfw'] else '否'}\n"
        if info.get('date'):
            output += f"  - 开播日期: {info['date']}\n"
        output += \
            f"  - 平台: {info['platform']}\n"\
            f"  - 标签: {', '.join(tags)}\n"\
            f"  - 元标签: {', '.join(info.get('meta_tag', []))}\n"\
            f"  - 集数: {info['eps']}\n"\
            f"  - 卷数: {info['volumes']}\n"\
            f"  - 简介: {info['summary']}\n"
        output += indent_text(parse_image_urls(info))
        output += \
            f"  - 评分: {rating.get('score', 'N/A')} ({rating.get('total', 'N/A')}人)\n"\
            f"  - 排名: {rating.get('rank', 'N/A')}\n"\
            f"  - 评分分布:\n"
        for key, value in rating.get('count', {}).items():
            output += f"    - {key}: {value}人\n"
        collection = info.get('collection', {})
        output += f"  - 收藏状态:\n"
        for key, value in collection.items():
            output += f"    - {collection_translations.get(key, key)}: {value}\n"
        #   if info.get('infobox'):
        #       output += f"  - 其他信息:\n"
        #       for detailed_info in info['infobox']:
        #           key = detailed_info.get('key', '未知')
        #           value = detailed_info.get('value', '无')
        #           if isinstance(value, str):
        #               output += f"    - {key}: {value}\n"

    return output


def parse_slim_subject_info(info: dict) -> str:
    """
    解析简化条目信息为字符串格式
    """
    
    summary = info['short_summary'][:100] + "..." if len(info['short_summary']) > 100 else info['short_summary']
    tags = [f"{tag['name']}({tag['count']})" for tag in info['tags']]
    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {subject_types.get(info['type'], '未知')}\n"
    if info.get('date'):
        output += f"  - 开播日期: {info['date']}\n"
    output += \
        f"  - 简介: {summary}\n"\
        f"  - 标签: {', '.join(tags)}\n"\
        f"  - 集数: {info['eps']}\n"\
        f"  - 卷数: {info['volumes']}\n"
    output += indent_text(parse_image_urls(info))
    output += \
        f"  - 评分: {info['score']} ({info.get('rating_count', 'N/A')}人)\n"\
        f"  - 排名: {info['rank']}\n"\
        f"  - 收藏总数: {info['collection_total']}\n"

    return output


def parse_subject_relation_info(info: dict) -> str:
    """
    解析条目相关信息为字符串格式
    """
    images = info.get('images', None)
    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {subject_types.get(info['type'], '未知')}\n"\
        f"  - 关系: {info['relation']}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_related_subject_info(info: dict) -> str:
    """
    解析相关条目信息为字符串格式
    """

    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {subject_types.get(info['type'], '未知')}\n"\
        f"  - 戏份: {', '.join(info['staff'])}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_related_person_info(info: dict) -> str:
    """
    解析条目人员信息为字符串格式
    """
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {person_types.get(info['type'], '未知')}\n"\
        f"  - 职业: {', '.join(info['career'])}\n"\
        f"  - 关系: {info['relation']}\n"\
        f"  - 参与集数: {info['eps']}\n"
    output += indent_text(parse_image_urls(info))
    
    return output


def parse_person_info(info: dict) -> str:
    """
    解析人员信息为字符串格式
    """
    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {person_types.get(info['type'], '未知')}\n"\
        f"  - 职业: {', '.join(info['career'])}\n"\
        f"  - 简介: {info['short_summary']}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_person_detail_info(info: dict) -> str:
    """
    解析人员详细信息为字符串格式
    """
    output = \
        f"- {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {person_types.get(info['type'], '未知')}\n"\
        f"  - 职业: {', '.join(info['career'])}\n"\
        f"  - 简介: {info['summary']}\n"
    if info.get('gender'):
        output += f"  - 性别: {info['gender']}\n"
    if info.get('blood_type'):
        output += f"  - 血型: {info['blood_type']}\n"
    birth_info = {}
    if info.get('birth_year'):
        birth_info['year'] = info['birth_year']
    if info.get('birth_mon'):
        birth_info['month'] = info['birth_mon']
    if info.get('birth_day'):
        birth_info['day'] = info['birth_day']
    if birth_info:
        birth_str = f"{birth_info.get('year', '未知')}年{birth_info.get('month', '未知')}月{birth_info.get('day', '未知')}日"
        output += f"  - 生日: {birth_str}\n"
    output += indent_text(parse_image_urls(info))
    stat = info.get('stat', {})
    output += f"  - 状态:\n"\
        f"    - 评论数: {stat['comments']}\n"\
        f"    - 收藏数: {stat['collects']}\n"

    return output


def parse_person_character_info(info: dict) -> str:
    """
    解析人员相关角色信息为字符串格式
    """
    subject_name = info.get('subject_name', 'N/A')
    subject_name_cn = info.get('subject_name_cn', 'N/A')
    subject_id = info.get('subject_id', 'N/A')
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {character_types.get(info['type'], '未知')}\n"\
        f"  - 相关条目: {subject_name} (中文名: {subject_name_cn}, ID: {subject_id})\n"\
        f"  - 条目类型: {subject_types.get(info['subject_type'], '未知')}\n"
    if info.get('staff'):
        output += f"  - 戏份: {', '.join(info['staff'])}\n"
    output += indent_text(parse_image_urls(info))

    return output

def parse_related_character_info(info: dict) -> str:
    """
    解析条目角色信息为字符串格式
    """
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {character_types.get(info['type'], '未知')}\n"\
        f"  - 关系: {info['relation']}\n"
    if info.get('actors'):
        output += f"  - 演员:\n"
        for actor in info['actors']:
            output += indent_text(parse_person_info(actor), indent=4)
    output += indent_text(parse_image_urls(info))
    
    return output


def parse_character_info(info: dict) -> str:
    """
    解析角色信息为字符串格式
    """
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {character_types.get(info['type'], '未知')}\n"\
        f"  - 简介: {info['summary']}\n"
    if info.get('gender'):
        output += f"  - 性别: {info['gender']}\n"
    if info.get('blood_type'):
        output += f"  - 血型: {info['blood_type']}\n"
    birth_info = {}
    if info.get('birth_year'):
        birth_info['year'] = info['birth_year']
    if info.get('birth_mon'):
        birth_info['month'] = info['birth_mon']
    if info.get('birth_day'):
        birth_info['day'] = info['birth_day']
    if birth_info:
        birth_str = f"{birth_info.get('year', '未知')}年{birth_info.get('month', '未知')}月{birth_info.get('day', '未知')}日"
        output += f"  - 生日: {birth_str}\n"
    output += f"  - 状态:\n"
    stat = info['stat']
    output += indent_text(parse_image_urls(info))
    if stat.get('comments'):
        output += f"    - 评论数: {stat['comments']}\n"
    if stat.get('collects'):
        output += f"    - 收藏数: {stat['collects']}\n"
    #   if info.get('infobox'):
    #       output += f"  - 其他信息:\n"
    #       for detailed_info in info['infobox']:
    #           key = detailed_info.get('key', '未知')
    #           value = detailed_info.get('value', '无')
    #           if isinstance(value, str):
    #               output += f"    - {key}: {value}\n"

    return output


def parse_character_person_info(info: dict) -> str:
    """
    解析角色相关人员信息为字符串格式
    """
    subject_name = info.get('subject_name', 'N/A')
    subject_name_cn = info.get('subject_name_cn', 'N/A')
    subject_id = info.get('subject_id', 'N/A')
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 类型: {character_types.get(info['type'], '未知')}\n"\
        f"  - 相关条目: {subject_name} (中文名: {subject_name_cn}, ID: {subject_id})\n"\
        f"  - 条目类型: {subject_types.get(info['subject_type'], '未知')}\n"
    if info.get('staff'):
        output += f"  - 戏份: {', '.join(info['staff'])}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_episode_info(info: dict) -> str:
    """
    解析集数信息为字符串格式
    """
    output = f"- 名称: {info.get('name', 'N/A')} (中文名: {info.get('name_cn', 'N/A')}, ID: {info.get('id', 'N/A')})\n"
    if info.get('ep'):
        output += f"  - 集数: {info['ep']}\n"
    output += \
        f"  - 类型: {episode_types.get(info['type'], '未知')}\n"\
        f"  - 音乐曲目碟片数: {info['disc']}\n"\
        f"  - 简介: {info['desc']}\n"\
        f"  - 评论数: {info['comment']}\n"\
        f"  - 所属条目ID: {info['subject_id']}\n"
    if info.get('airdate'):
        output += f"  - 首映日期: {info['airdate']}\n"
    if info.get('duration'):
        output += f"  - 时长: {info['duration']}分钟\n"

    return output


def parse_user_info(info: dict) -> str:
    """
    解析用户信息为字符串格式
    """
    group = user_group.get(info['user_group'], '未知')
    output = \
        f"- 用户名: {info.get('username', 'N/A')}\n"\
        f"  - 昵称: {info['nickname']}\n"\
        f"  - 用户ID: {info['id']}\n"\
        f"  - 用户组: {group}\n"\
        f"  - 签名: {info['sign']}\n"
    
    return output


def parse_user_subject_collection_info(info: dict) -> str:
    """
    解析用户收藏信息为字符串格式
    """
    subject_type = subject_types.get(info['subject_type'], '未知')
    collection_type = collection_types.get(info['type'], '未知')
    output = \
        f"- ID: {info['subject_id']}\n"\
        f"  - 条目类型: {subject_type}\n"\
        f"  - 更新时间: {info['updated_at']}\n"\
        f"  - 标签: {', '.join(info['tags'])}\n"\
        f"  - 当前卷数: {info['vol_status']}\n"\
        f"  - 当前集数: {info['ep_status']}\n"\
        f"  - 收藏类型: {collection_type}\n"
    if info.get('comment'):
        output += f"  - 评价: {info['comment']}\n"
    if info.get('subject'):
        subject_info = info['subject']
        output += f"  - 条目信息:\n"
        output += indent_text(parse_slim_subject_info(subject_info), indent=4)
    
    return output


def parse_user_episode_collection_info(info: dict) -> str:
    """
    解析用户集数收藏信息为字符串格式
    """
    output = f"- 剧集信息:\n"
    output += indent_text(parse_episode_info(info.get('episode', {})))
    output += \
        f"- 收藏类型: {episode_collection_types.get(info.get('type', 0), '未知')}\n"\
        f"- 更新时间: {info.get('updated_at', '未知')}\n"
    
    return output


def parse_user_character_collection_info(info: dict) -> str:
    """
    解析用户角色收藏信息为字符串格式
    """
    character_type = character_types.get(info['type'], '未知')
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 角色类型: {character_type}\n"\
        f"  - 更新时间: {info['updated_at']}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_user_person_collection_info(info: dict) -> str:
    """
    解析用户人员收藏信息为字符串格式
    """
    person_type = person_types.get(info['type'], '未知')
    output = \
        f"- {info.get('name', 'N/A')} (ID: {info.get('id', 'N/A')})\n"\
        f"  - 人员类型: {person_type}\n"\
        f"  - 更新时间: {info['updated_at']}\n"\
        f"  - 职业: {', '.join(info.get('career', []))}\n"
    output += indent_text(parse_image_urls(info))

    return output


def parse_error_info(error: dict) -> str:
    """
    解析错误信息为字符串格式
    """
    output = \
        f"- 错误标题: {error['title']}\n"\
        f"  - 错误描述: {error['description']}\n"
    if error.get('details'):
        output += f"  - 详细信息: {error['details']}\n"

    return output
import logging
from datetime import datetime
from jsonschema import validate
import mcp.types as types
from . import utils
from .bangumi_client import BangumiClient


logger = logging.getLogger(__name__)


# Initialize Bangumi client
try:
    bangumi_client = BangumiClient()
except Exception as e:
    logger.error(f"Failed to initialize Bangumi client: {e}")
    raise RuntimeError("Bangumi client initialization failed") from e


async def get_current_time(arguments):
    """
    [GET] /current_time 获取当前时间
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    weakday = datetime.now().strftime("%A")

    return [types.TextContent(type="text", text=f"当前时间: {now}，星期: {weakday}")]


#-------------------------条目-------------------------
async def get_calendar(arguments):
    """
    [GET] /calendar 每日放送
    """
    status_code, calendar = await bangumi_client.get_calendar()

    if status_code >= 400:
        assert isinstance(calendar, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(calendar)}\n"
        return [types.TextContent(type="text", text=output)]
    
    assert isinstance(calendar, list), "Calendar data should be a list"
    output = "每周放送时间表:\n\n"
    for day in calendar:
        weekday = day.get('weekday', {})
        day_name = weekday.get('cn', weekday.get('en', 'Unknown'))
        items = day.get('items', [])
        
        output += f"{day_name} ({len(items)} 部):\n"
        for item in items:
            output += utils.indent_text(utils.parse_lagacy_subject_small_info(item))
    
    return [types.TextContent(type="text", text=output)]


async def search_subjects(arguments):
    """
    [POST] /v0/search/subjects 搜索条目
    """
    status_code, results = await bangumi_client.search_subjects(arguments)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get('data', [])
    output = f"找到 {results.get('total', 'N/A')} 条结果:\n\n"
    for item in items:
        output += utils.parse_subject_info(item, brief=True)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_subjects(arguments):
    """
    [GET] /v0/subjects 浏览条目
    通过类型和分页获取条目列表
    """

    status_code, results = await bangumi_client.get_subjects(arguments)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get("data", [])
    output = f"找到 {results.get('total', 'N/A')} 条结果:\n\n"
    for item in items:
        output += utils.parse_subject_info(item, brief=True)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_subject_info(arguments):
    """
    [GET] /v0/subjects/{subject_id} 获取条目详细信息
    """
    subject_id = arguments.get("subject_id")

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, info = await bangumi_client.get_subject_info(subject_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_subject_info(info)
    
    return [types.TextContent(type="text", text=output)]


async def get_subject_image(arguments):
    """
    [GET] /v0/subjects/{subject_id}/image 获取条目图片
    """
    subject_id = arguments.get("subject_id")
    type = arguments.get("type")

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    if type not in ["small", "grid", "large", "medium", "common"]:
        return [types.TextContent(
            type="text",
            text="Error: type parameter must be one of ['small', 'grid', 'large', 'medium', 'common']"
        )]

    params = {
        "type": type
    }

    status_code, image = await bangumi_client.get_subject_image(subject_id, params)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(image)}\n"
    else:
        output = f"![条目 {subject_id} 图片 ({type})]({image['url']})\n"

    return [types.TextContent(type="text", text=output)]


async def get_subject_persons(arguments):
    """
    [GET] /v0/subjects/{subject_id}/persons 获取条目人员信息
    """
    subject_id = arguments.get("subject_id")

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, persons = await bangumi_client.get_subject_persons(subject_id)

    if status_code >= 400:
        assert isinstance(persons, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(persons)}\n"
        return [types.TextContent(type="text", text=output)]
    
    assert isinstance(persons, list), "Persons data should be a list"
    output = f"条目 {subject_id} 人员信息:\n\n"
    for person in persons:
        output += utils.parse_related_person_info(person)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


async def get_subject_characters(arguments):
    """
    [GET] /v0/subjects/{subject_id}/characters 获取条目角色信息
    """
    args = arguments or {}
    subject_id = args.get("subject_id")
    
    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, characters = await bangumi_client.get_subject_characters(subject_id)

    if status_code >= 400:
        assert isinstance(characters, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(characters)}\n"
        return [types.TextContent(type="text", text=output)]

    assert isinstance(characters, list), "Characters data should be a list"
    output = f"条目 {subject_id} 角色信息:\n\n"
    for character in characters:
        output += utils.parse_related_character_info(character)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


async def get_subject_relations(arguments):
    """
    [GET] /v0/subjects/{subject_id}/subjects 获取条目相关条目
    """
    args = arguments or {}
    subject_id = args.get("subject_id")
    
    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, relations = await bangumi_client.get_subject_relations(subject_id)

    if status_code >= 400:
        assert isinstance(relations, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(relations)}\n"
        return [types.TextContent(type="text", text=output)]
    
    assert isinstance(relations, list), "Relations data should be a list"
    output = f"条目 {subject_id} 相关条目:\n\n"
    for relation in relations:
        output += utils.parse_subject_relation_info(relation)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


#-------------------------剧集-------------------------
async def get_episodes(arguments):
    """
    [GET] /v0/episodes 获取条目剧集信息
    """
    subject_id = arguments.get("subject_id")
    
    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, episodes = await bangumi_client.get_episodes(arguments)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(episodes)}\n"
        return [types.TextContent(type="text", text=output)]

    output = f"条目 {subject_id} 剧集信息:\n\n"
    for episode in episodes.get('data', []):
        output += utils.parse_episode_info(episode)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


async def get_episode_info(arguments):
    """
    [GET] /v0/episodes/{episode_id} 获取某集信息
    """
    args = arguments or {}
    episode_id = args.get("episode_id")

    if not episode_id:
        return [types.TextContent(
            type="text",
            text="Error: episode_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_episode_info(episode_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_episode_info(info)

    return [types.TextContent(type="text", text=output)]


#-------------------------角色-------------------------
async def search_characters(arguments):
    """
    [POST] /v0/search/characters 搜索角色
    """
    status_code, results = await bangumi_client.search_characters(arguments)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get('data', [])
    output = f"找到 {results.get('total', 'N/A')} 条结果:\n\n"
    for item in items:
        output += utils.parse_character_info(item)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_character_info(arguments):
    """
    [GET] /v0/characters/{character_id} 获取角色信息
    """
    args = arguments or {}
    character_id = args.get("character_id")

    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_character_info(character_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(info)}\n"
        return [types.TextContent(type="text", text=output)]

    output = utils.parse_character_info(info)

    return [types.TextContent(type="text", text=output)]


async def get_character_subjects(arguments):
    """
    [GET] /v0/characters/{character_id}/subjects 获取角色相关条目
    """
    args = arguments or {}
    character_id = args.get("character_id")

    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, subjects = await bangumi_client.get_character_subjects(character_id)

    if status_code >= 400:
        assert isinstance(subjects, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(subjects)}\n"
        return [types.TextContent(type="text", text=output)]

    assert isinstance(subjects, list), "Subjects data should be a list"
    output = f"角色 {character_id} 相关条目:\n\n"
    for subject in subjects:
        output += utils.parse_related_subject_info(subject)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_character_persons(arguments):
    """
    [GET] /v0/characters/{character_id}/persons 获取角色相关人员
    """
    args = arguments or {}
    character_id = args.get("character_id")

    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, persons = await bangumi_client.get_character_persons(character_id)

    if status_code >= 400:
        assert isinstance(persons, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(persons)}\n"
        return [types.TextContent(type="text", text=output)]

    assert isinstance(persons, list), "Persons data should be a list"
    output = f"角色 {character_id} 相关人员:\n\n"
    for person in persons:
        output += utils.parse_person_info(person)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def post_character_collection(arguments):
    """
    [POST] /v0/characters/{character_id}/collect 收藏角色
    """
    args = arguments or {}
    character_id = args.get("character_id")

    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, result = await bangumi_client.post_character_collection(character_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(result)}\n"
    else:
        output = f"角色 {character_id} 收藏成功!\n\n"

    return [types.TextContent(type="text", text=output)]


async def delete_character_collection(arguments):
    """
    [DELETE] /v0/characters/{character_id}/collect 取消收藏角色
    """
    args = arguments or {}
    character_id = args.get("character_id")

    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, result = await bangumi_client.delete_character_collection(character_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(result)}\n"
    else:
        output = f"角色 {character_id} 取消收藏成功!\n\n"

    return [types.TextContent(type="text", text=output)]


#-------------------------人员-------------------------
async def search_persons(arguments):
    """
    [POST] /v0/search/persons 搜索人员
    """
    status_code, results = await bangumi_client.search_persons(arguments)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get('data', [])
    output = f"找到 {results.get('total', 'N/A')} 条结果:\n\n"
    for item in items:
        output += utils.parse_person_info(item)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_person_info(arguments):
    """
    [GET] /v0/persons/{person_id} 获取人员信息
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_person_info(person_id)

    if status_code >= 400:
        output = f"错误详情:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_person_info(info)

    return [types.TextContent(type="text", text=output)]


async def get_person_subjects(arguments):
    """
    [GET] /v0/persons/{person_id}/subjects 获取人员相关条目
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, subjects = await bangumi_client.get_person_subjects(person_id)

    if status_code >= 400:
        assert isinstance(subjects, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(subjects)}\n"
        return [types.TextContent(type="text", text=output)]

    assert isinstance(subjects, list), "Subjects data should be a list"
    output = f"人员 {person_id} 相关条目:\n\n"
    for subject in subjects:
        output += utils.parse_subject_info(subject)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def get_person_characters(arguments):
    """
    [GET] /v0/persons/{person_id}/characters 获取人员相关角色
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, characters = await bangumi_client.get_person_characters(person_id)

    if status_code >= 400:
        assert isinstance(characters, dict), "Error response should be a dictionary"
        output = f"错误详情:\n\n{utils.parse_error_info(characters)}\n"
        return [types.TextContent(type="text", text=output)]

    assert isinstance(characters, list), "Characters data should be a list"
    output = f"人员 {person_id} 相关角色:\n\n"
    for character in characters:
        output += utils.parse_person_character_info(character)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def post_person_collection(arguments):
    """
    [POST] /v0/persons/{person_id}/collect 收藏人员
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, result = await bangumi_client.post_person_collection(person_id)

    if status_code >= 400:
        output = f"错误详情**:\n\n{utils.parse_error_info(result)}\n"
    else:
        output = f"人员 {person_id} 收藏成功!\n\n"

    return [types.TextContent(type="text", text=output)]


async def delete_person_collection(arguments):
    """
    [DELETE] /v0/persons/{person_id}/collect 取消收藏人员
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, result = await bangumi_client.delete_person_collection(person_id)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(result)}\n"
    else:
        output = f"人员 {person_id} 取消收藏成功!\n\n"

    return [types.TextContent(type="text", text=output)]


#-------------------------用户-------------------------
async def get_user_info(arguments):
    """
    [GET] /v0/users/{username} 获取用户信息
    """
    username = arguments.get("username")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]

    status_code, info = await bangumi_client.get_user_info(username)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_info(info)

    return [types.TextContent(type="text", text=output)]


async def get_me_info(arguments):
    """
    [GET] /v0/users/me 获取当前用户信息
    """
    status_code, info = await bangumi_client.get_me_info()

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_info(info)

    return [types.TextContent(type="text", text=output)]


#-------------------------收藏-------------------------
async def get_user_collections(arguments):
    username = arguments.get("username", "")
    params = arguments.get("params", {})

    status_code, results = await bangumi_client.get_user_collections(
        username=username,
        params=params
    )

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get("data", [])

    output = f"找到 {results.get('total', 'N/A')} 个结果:\n\n"
    for item in items:
        output += utils.parse_user_subject_collection_info(item)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


async def get_user_collection_info(arguments):
    """
    [GET] /v0/users/{username}/collections/{subject_id} 获取用户指定收藏条目
    """
    username = arguments.get("username")
    subject_id = arguments.get("subject_id")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_user_collection_info(username, subject_id)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_subject_collection_info(info)

    return [types.TextContent(type="text", text=output)]


async def post_my_collection(arguments):
    """
    [POST] /v0/users/-/collections/{subject_id} 收藏条目
    """
    subject_id = arguments.get("subject_id")
    params = arguments.get("params", {})

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]

    status_code, info = await bangumi_client.post_my_collection(subject_id, params)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = f"条目 {subject_id} 收藏成功!\n\n"

    return [types.TextContent(type="text", text=output)]


async def patch_my_collection(arguments):
    """
    [PATCH] /v0/users/-/collections/{subject_id} 更新用户条目收藏
    """
    subject_id = arguments.get("subject_id")
    params = arguments.get("params", {})

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]

    status_code, info = await bangumi_client.patch_my_collection(subject_id, params)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = f"条目 {subject_id} 收藏更新成功!\n\n"

    return [types.TextContent(type="text", text=output)]


async def get_my_episode_collections(arguments):
    """
    [GET] /v0/users/-/collections/{subject_id}/episodes 获取用户剧集收藏
    """
    subject_id = arguments.get("subject_id")
    params = arguments.get("params", {})

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]

    status_code, results = await bangumi_client.get_my_episode_collections(subject_id, params)

    items = results.get("data", [])

    output = f"找到 {results.get('total', 'N/A')} 个结果:\n\n"
    for item in items:
        output += utils.parse_user_episode_collection_info(item)
    output += "\n"

    return [types.TextContent(type="text", text=output)]


async def patch_my_episode_collections(arguments):
    """
    [PATCH] /v0/users/-/collections/{subject_id}/episodes 更新用户剧集收藏
    """
    subject_id = arguments.get("subject_id")
    episode_id = arguments.get("episode_id")
    type = arguments.get("type")

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    if not episode_id:
        return [types.TextContent(
            type="text",
            text="Error: episode_id parameter is required"
        )]
    if type is None:
        return [types.TextContent(
            type="text",
            text="Error: type parameter is required"
        )]
    
    params = {
        "episode_id": episode_id,
        "type": type
    }

    status_code, results = await bangumi_client.patch_my_episode_collections(subject_id, params)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(results)}\n"
    else:
        output = f"剧集 {subject_id} 收藏更新成功!\n\n"

    return [types.TextContent(type="text", text=output)]


async def get_my_episode_collection_info(arguments):
    """
    [GET] /v0/users/-/collections/-/episodes/{episode_id} 获取用户指定剧集收藏
    """
    episode_id = arguments.get("episode_id")

    if not episode_id:
        return [types.TextContent(
            type="text",
            text="Error: episode_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_my_episode_collection_info(episode_id)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_episode_collection_info(info)

    return [types.TextContent(type="text", text=output)]

async def put_my_episode_collection_info(arguments):
    """
    [PUT] /v0/users/-/collections/-/episodes/{episode_id} 更新用户剧集收藏
    """
    episode_id = arguments.get("episode_id")
    type = arguments.get("type", {})

    if not episode_id:
        return [types.TextContent(
            type="text",
            text="Error: episode_id parameter is required"
        )]
    if type is None:
        return [types.TextContent(
            type="text",
            text="Error: type parameter is required"
        )]
    
    params = {
        "type": type
    }

    status_code, info = await bangumi_client.put_my_episode_collection_info(episode_id, params)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = f"剧集 {episode_id} 收藏更新成功!\n\n"

    return [types.TextContent(type="text", text=output)]

async def get_user_character_collections(arguments):
    """
    [GET] /v0/users/{username}/collections/-/characters 获取用户角色收藏
    """
    username = arguments.get("username")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]

    status_code, results = await bangumi_client.get_user_character_collections(username=username)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get("data", [])

    output = f"找到 {results.get('total', 'N/A')} 个结果:\n\n"
    for item in items:
        output += utils.parse_user_character_collection_info(item)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]

async def get_user_character_collection_info(arguments):
    """
    [GET] /v0/users/{username}/collections/-/characters/{character_id} 获取用户指定角色收藏
    """
    username = arguments.get("username")
    character_id = arguments.get("character_id")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]
    
    if not character_id:
        return [types.TextContent(
            type="text",
            text="Error: character_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_user_character_collection_info(username, character_id)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_character_collection_info(info)

    return [types.TextContent(type="text", text=output)]


async def get_user_person_collections(arguments):
    """
    [GET] /v0/users/{username}/collections/-/persons 获取用户人员收藏
    """
    username = arguments.get("username")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]

    status_code, results = await bangumi_client.get_user_person_collections(username=username)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(results)}\n"
        return [types.TextContent(type="text", text=output)]

    items = results.get("data", [])

    output = f"找到 {results.get('total', 'N/A')} 个结果:\n\n"
    for item in items:
        output += utils.parse_user_person_collection_info(item)
    output += "\n"
    
    return [types.TextContent(type="text", text=output)]


async def get_user_person_collection_info(arguments):
    """
    [GET] /v0/users/{username}/collections/-/persons/{person_id} 获取用户指定人员收藏
    """
    username = arguments.get("username")
    person_id = arguments.get("person_id")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]
    
    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_user_person_collection_info(username, person_id)

    if status_code >= 400:
        output = f"**错误详情**:\n\n{utils.parse_error_info(info)}\n"
    else:
        output = utils.parse_user_person_collection_info(info)

    return [types.TextContent(type="text", text=output)]
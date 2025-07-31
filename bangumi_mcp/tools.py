import logging
from datetime import datetime
from jsonschema import validate
import mcp.types as types
import json
from .bangumi_client import BangumiClient
from .utils import remove_null_items


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

    return {"calendar": calendar}


async def search_subjects(arguments):
    """
    [POST] /v0/search/subjects 搜索条目
    """
    status_code, results = await bangumi_client.search_subjects(arguments)

    return remove_null_items(results)


async def get_subjects(arguments):
    """
    [GET] /v0/subjects 浏览条目
    通过类型和分页获取条目列表
    """

    status_code, results = await bangumi_client.get_subjects(arguments)

    return remove_null_items(results)


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

    return remove_null_items(info)

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

    status_code, image = await bangumi_client.get_subject_image(subject_id, {"type": type})


    if status_code >= 400:
        return image
    else:
        #output = f"![条目 {subject_id} 图片 ({type})]({image['url']})\n"
        return {"url": image["url"], "type": type}


async def get_subject_persons(arguments):
    """
    [GET] /v0/subjects/{subject_id}/persons 获取条目人物信息
    """
    subject_id = arguments.get("subject_id")

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, persons = await bangumi_client.get_subject_persons(subject_id)

    if status_code >= 400:
        return persons
    else:
        return {"related_persons": persons}


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
        return characters
    else:
        return {"related_characters": characters}


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
        return relations
    else:
        return {"subject_relations": relations}


#-------------------------剧集/章节-------------------------
async def get_episodes(arguments):
    """
    [GET] /v0/episodes 获取条目剧集/章节信息
    """
    subject_id = arguments.get("subject_id")
    
    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]
    
    status_code, episodes = await bangumi_client.get_episodes(arguments)

    return remove_null_items(episodes)


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

    return remove_null_items(info)


#-------------------------角色-------------------------
async def search_characters(arguments):
    """
    [POST] /v0/search/characters 搜索角色
    """
    status_code, results = await bangumi_client.search_characters(arguments)

    return remove_null_items(results)


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

    return remove_null_items(info)


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
        return subjects
    else:
        return {"related_subjects": subjects}


async def get_character_persons(arguments):
    """
    [GET] /v0/characters/{character_id}/persons 获取角色相关人物
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
        return persons
    else:
        return {"related_persons": persons}


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
        return result
    else:
        return {"info": f"角色 {character_id} 收藏成功!"}


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
        return result
    else:
        return {"info": f"角色 {character_id} 取消收藏成功!"}


#-------------------------人物-------------------------
async def search_persons(arguments):
    """
    [POST] /v0/search/persons 搜索人物
    """
    status_code, results = await bangumi_client.search_persons(arguments)

    return remove_null_items(results)


async def get_person_info(arguments):
    """
    [GET] /v0/persons/{person_id} 获取人物信息
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_person_info(person_id)

    return remove_null_items(info)


async def get_person_subjects(arguments):
    """
    [GET] /v0/persons/{person_id}/subjects 获取人物相关条目
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, subjects = await bangumi_client.get_person_subjects(person_id)

    if status_code >= 400:
        return subjects
    else:
        return {"related_subjects": subjects}


async def get_person_characters(arguments):
    """
    [GET] /v0/persons/{person_id}/characters 获取人物相关角色
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, characters = await bangumi_client.get_person_characters(person_id)

    if status_code >= 400:
        return characters
    else:
        return {"related_characters": characters}


async def post_person_collection(arguments):
    """
    [POST] /v0/persons/{person_id}/collect 收藏人物
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, result = await bangumi_client.post_person_collection(person_id)

    if status_code >= 400:
        return result
    else:
        return {"info": f"人物 {person_id} 收藏成功!"}


async def delete_person_collection(arguments):
    """
    [DELETE] /v0/persons/{person_id}/collect 取消收藏人物
    """
    person_id = arguments.get("person_id")

    if not person_id:
        return [types.TextContent(
            type="text",
            text="Error: person_id parameter is required"
        )]

    status_code, result = await bangumi_client.delete_person_collection(person_id)

    if status_code >= 400:
        return result
    else:
        return {"info": f"人物 {person_id} 取消收藏成功！"}


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

    return remove_null_items(info)


async def get_me_info(arguments):
    """
    [GET] /v0/users/me 获取当前用户信息
    """
    status_code, info = await bangumi_client.get_me_info()

    return remove_null_items(info)


#-------------------------收藏-------------------------
async def get_user_collections(arguments):
    username = arguments.get("username", "")
    params = arguments.get("params", {})

    status_code, results = await bangumi_client.get_user_collections(
        username=username,
        params=params
    )

    return remove_null_items(results)


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

    return remove_null_items(info)


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
        return info
    else:
        return {"info": f"条目 {subject_id} 收藏成功!"}


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
        return info
    else:
        return {"info": f"条目 {subject_id} 收藏更新成功!"}


async def get_my_episode_collections(arguments):
    """
    [GET] /v0/users/-/collections/{subject_id}/episodes 获取用户剧集/章节收藏
    """
    subject_id = arguments.get("subject_id")
    params = arguments.get("params", {})

    if not subject_id:
        return [types.TextContent(
            type="text",
            text="Error: subject_id parameter is required"
        )]

    status_code, results = await bangumi_client.get_my_episode_collections(subject_id, params)

    return remove_null_items(results)


async def patch_my_episode_collections(arguments):
    """
    [PATCH] /v0/users/-/collections/{subject_id}/episodes 更新用户剧集/章节收藏
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
        return results
    else:
        return {"info": f"条目 {subject_id} 的剧集/章节 {episode_id} 收藏更新成功!"}


async def get_my_episode_collection_info(arguments):
    """
    [GET] /v0/users/-/collections/-/episodes/{episode_id} 获取用户指定剧集/章节收藏
    """
    episode_id = arguments.get("episode_id")

    if not episode_id:
        return [types.TextContent(
            type="text",
            text="Error: episode_id parameter is required"
        )]

    status_code, info = await bangumi_client.get_my_episode_collection_info(episode_id)

    return remove_null_items(info)


async def put_my_episode_collection_info(arguments):
    """
    [PUT] /v0/users/-/collections/-/episodes/{episode_id} 更新用户剧集/章节收藏
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
        return info
    else:
        return {"info": f"剧集/章节 {episode_id} 收藏更新成功!"}


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

    return remove_null_items(results)


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

    return remove_null_items(info)


async def get_user_person_collections(arguments):
    """
    [GET] /v0/users/{username}/collections/-/persons 获取用户人物收藏
    """
    username = arguments.get("username")

    if not username:
        return [types.TextContent(
            type="text",
            text="Error: username parameter is required"
        )]

    status_code, results = await bangumi_client.get_user_person_collections(username=username)

    return remove_null_items(results)


async def get_user_person_collection_info(arguments):
    """
    [GET] /v0/users/{username}/collections/-/persons/{person_id} 获取用户指定人物收藏
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

    return remove_null_items(info)
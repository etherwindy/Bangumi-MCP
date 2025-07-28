import mcp.types as types

tool_list = [
        types.Tool(
            name="get_current_time",
            description="获取当前时间",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_calendar",
            description="获取放送时间表",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="search_subjects",
            description="搜索条目（可以是书籍、动画、音乐、游戏、三次元内容等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "sort": {
                        "type": "string",
                        "description": "排序方式：date=按日期排序，rank=按排名排序",
                        "default": None
                    },
                    "filter": {
                        "type": "object",
                        "description": "过滤条件，没有则不使用",
                        "properties": {
                            "type": {
                                "type": "array",
                                "description": "条目类型过滤，1=书籍，2=动画，3=音乐，4=游戏，6=三次元，没有5",
                                "items": {
                                    "type": "integer"
                                }
                            },
                            "meta_tags": {
                                "type": "array",
                                "description": "元标签过滤",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "tags": {
                                "type": "array",
                                "description": "标签过滤",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "air_date": {
                                "type": "array",
                                "description": "首映日期范围过滤，格式为 > / < / =< / >= YYYY-MM-DD，例如 '>2023-01-01, <=2023-12-31'",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "rating": {
                                "type": "array",
                                "description": "评分范围过滤，格式为 > / < / =< / >= 分数，例如 '>8, <=9'",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "rank": {
                                "type": "array",
                                "description": "排名范围过滤，格式为 > / < / =< / >= 排名，例如 '>1000, <=5000'",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "nsfw": {
                                "type": "boolean",
                                "description": "是否包含NSFW内容，默认 False（不包含）",
                                "default": False
                            }
                        },
                        "default": {}
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制，默认30",
                        "default": 30
                    },
                    "offset": {
                        "type": "integer",
                        "description": "分页偏移量，默认0",
                        "default": 0
                    }
                },
                "required": ["keyword"]
            }
        ),
        types.Tool(
            name="get_subjects",
            description="浏览条目",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "integer",
                        "description": "条目类型：1=书籍，2=动画，3=音乐，4=游戏，6=三次元，没有5",
                        "default": None
                    },
                    "cat": {
                        "type": "integer",
                        "description": "可选类型：\n"
                        "书籍类型：0=其他，1001=漫画，1002=小说，1003=画集\n"
                        "动画类型：0=其他，1=TV，2=OVA，3=Movie，5=WEB\n"
                        "游戏类型：0=其他，4001=游戏，4002=软件，4003=拓展包，4005=桌游\n"
                        "电影类型：0=其他，1=日剧，2=欧美剧，3=华语剧，6001=电视剧，6002=电影，6003=演出，6004=综艺\n",
                        "default": None
                    },
                    "series": {
                        "type": "boolean",
                        "description": "是否按系列分组，仅对书籍类型有效",
                        "default": False
                    },
                    "platform": {
                        "type": "string",
                        "description": "平台过滤，适用于游戏类型",
                        "default": None
                    },
                    "sort": {
                        "type": "string",
                        "description": "排序方式：\n"
                        "date=按日期排序，rank=按排名排序\n"
                        "默认 None（不排序）",
                        "default": None
                    },
                    "year": {
                        "type": "integer",
                        "description": "年份过滤",
                        "default": None
                    },
                    "month": {
                        "type": "integer",
                        "description": "月份过滤，1-12",
                        "default": None
                    },
                    "day": {
                        "type": "integer",
                        "description": "日期过滤，1-31",
                        "default": None
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制",
                        "default": 30
                    },
                    "offset": {
                        "type": "integer",
                        "description": "分页偏移量",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="get_subject_info",
            description="获取条目详细信息，仅在需要获得完整信息时使用",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    }
                },
                "required": ["subject_id"]
            }
        ),
        #   types.Tool(
        #       name="get_subject_image",
        #       description="获取条目图片 URL",
        #       inputSchema={
        #           "type": "object",
        #           "properties": {
        #               "subject_id": {
        #                   "type": "integer",
        #                   "description": "条目ID"
        #               },
        #               "type": {
        #                   "type": "string",
        #                   "description": "大小 {small|grid|large|medium|common}",
        #               },
        #           },
        #           "required": ["subject_id", "type"]
        #       }
        #   ),
        types.Tool(
            name="get_subject_persons",
            description="获取条目相关人员信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    }
                },
                "required": ["subject_id"]
            }
        ),
        types.Tool(
            name="get_subject_characters",
            description="获取条目角色信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    }
                },
                "required": ["subject_id"]
            }
        ),
        types.Tool(
            name="get_subject_relations",
            description="获取与输入条目相关的其他条目信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    }
                },
                "required": ["subject_id"]
            }
        ),
        types.Tool(
            name="get_episodes",
            description="获取条目剧集信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "episode_type": {
                        "type": "integer",
                        "description": "集数类型：0=本篇，1=特别篇，2=OP, 3=ED，4=预告/宣传/广告，5=MAD，6=其他",
                        "default": None
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制",
                        "default": 30
                    },
                    "offset": {
                        "type": "integer",
                        "description": "分页偏移量",
                        "default": 0
                    }
                },
                "required": ["subject_id"]
            }
        ),
        types.Tool(
            name="get_episode_info",
            description="获取某集信息，仅在需要获得完整信息时使用",
            inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {
                        "type": "integer",
                        "description": "剧集ID"
                    }
                },
                "required": ["episode_id"]
            }
        ),
        types.Tool(
            name="search_characters",
            description="搜索角色",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "filter": {
                        "type": "object",
                        "description": "过滤条件，没有则不使用",
                        "properties": {
                            "nsfw": {
                                "type": "boolean",
                                "description": "是否包含NSFW内容",
                                "default": False
                            }
                        },
                        "default": {}
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制",
                        "default": 30
                    },
                    "offset": {
                        "type": "integer",
                        "description": "分页偏移量",
                        "default": 0
                    }
                },
                "required": ["keyword"]
            }
        ),
        types.Tool(
            name="get_character_info",
            description="获取角色详细信息，仅在需要获得完整信息时使用",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_id": {
                        "type": "integer",
                        "description": "角色ID"
                    }
                },
                "required": ["character_id"]
            }
        ),
        types.Tool(
            name="get_character_subjects",
            description="获取角色相关条目信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_id": {
                        "type": "integer",
                        "description": "角色ID"
                    },
                },
                "required": ["character_id"]
            }
        ),
        types.Tool(
            name="get_character_persons",
            description="获取角色相关人员信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_id": {
                        "type": "integer",
                        "description": "角色ID"
                    }
                },
                "required": ["character_id"]
            }
        ),
        types.Tool(
            name="post_character_collection",
            description="为当前用户收藏角色",
            inputSchema={
                "type": "object",
                "properties": {
                    "character_id": {
                        "type": "integer",
                        "description": "角色ID"
                    },
                },
                "required": ["character_id"]
            }
        ),
        #   暂时不可用
        #   types.Tool(
        #       name="delete_character_collection",
        #       description="为当前用户取消收藏角色",
        #       inputSchema={
        #           "type": "object",
        #           "properties": {
        #               "character_id": {
        #                   "type": "integer",
        #                   "description": "角色ID"
        #               },
        #           },
        #           "required": ["character_id"]
        #       }
        #   ),
        types.Tool(
            name="search_persons",
            description="搜索人物",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "filter": {
                        "type": "object",
                        "description": "过滤条件，没有则不使用",
                        "properties": {
                            "nsfw": {
                                "type": "boolean",
                                "description": "是否包含NSFW内容",
                                "default": False
                            }
                        },
                        "default": {}
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制",
                        "default": 30
                    },
                    "offset": {
                        "type": "integer",
                        "description": "分页偏移量",
                        "default": 0
                    }
                },
                "required": ["keyword"]
            }
        ),
        types.Tool(
            name="get_person_info",
            description="获取人物详细信息，仅在需要获得完整信息时使用",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {
                        "type": "integer",
                        "description": "人物ID"
                    }
                },
                "required": ["person_id"]
            }
        ),
        types.Tool(
            name="get_person_subjects",
            description="获取人物相关条目列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {
                        "type": "integer",
                        "description": "人物ID"
                    },
                },
                "required": ["person_id"]
            }
        ),
        types.Tool(
            name="get_person_characters",
            description="获取人物相关角色列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {
                        "type": "integer",
                        "description": "人物ID"
                    }
                },
                "required": ["person_id"]
            }
        ),
        types.Tool(
            name="post_person_collection",
            description="为当前用户收藏人物",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {
                        "type": "integer",
                        "description": "人物ID"
                    },
                },
                "required": ["person_id"]
            }
        ),
        #   暂时不可用
        #   types.Tool(
        #       name="delete_person_collection",
        #       description="为当前用户取消收藏人物",
        #       inputSchema={
        #           "type": "object",
        #           "properties": {
        #               "person_id": {
        #                   "type": "integer",
        #                   "description": "人物ID"
        #               },
        #           },
        #           "required": ["person_id"]
        #       }
        #   ),
        types.Tool(
            name="get_user_info",
            description="获取用户信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    }
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_me_info",
            description="获取当前用户信息",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_user_collections",
            description="获取用户收藏信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                    "params": {
                        "type": "object",
                        "description": "可选参数，包含以下字段：",
                        "properties": {
                            "subject_type": {
                                "type": "integer",
                                "description": "条目类型：1=书籍，2=动画，3=音乐，4=游戏，6=三次元，没有5",
                                "default": None
                            },
                            "type": {
                                "type": "integer",
                                "description": "收藏类型：1=想看，2=看过，3=在看，4=搁置，5=抛弃",
                                "default": None
                            },
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制",
                                "default": 30
                            },
                            "offset": {
                                "type": "integer",
                                "description": "分页偏移量",
                                "default": 0
                            }
                        },
                        "default": {}
                    }
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_user_collection_info",
            description="获取用户指定条目信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    }
                },
                "required": ["username", "subject_id"]
            }
        ),
        types.Tool(
            name="post_my_collection",
            description="为当前用户收藏指定条目，如果已收藏则更新",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "params": {
                        "type": "object",
                        "description": "可选参数，包含以下字段：",
                        "properties": {
                            "type": {
                                "type": "integer",
                                "description": "收藏类型：1=想看，2=看过，3=在看，4=搁置，5=抛弃",
                            },
                            "tags": {
                                "type": "array",
                                "description": "标签列表，不传不作修改，空列表表示清空标签",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "comment": {
                                "type": "string",
                                "description": "评论内容"
                            }
                        },
                        "default": {}
                    }
                },
                "required": ["subject_id"]
            },
        ),
        types.Tool(
            name="post_my_collection",
            description="为当前用户更新指定收藏条目",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "params": {
                        "type": "object",
                        "description": "可选参数，包含以下字段：",
                        "properties": {
                            "type": {
                                "type": "integer",
                                "description": "收藏类型：1=想看，2=看过，3=在看，4=搁置，5=抛弃",
                            },
                            "tags": {
                                "type": "array",
                                "description": "标签列表，不传不作修改，空列表表示清空标签",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "comment": {
                                "type": "string",
                                "description": "评论内容"
                            }
                        },
                        "default": {}
                    }
                },
                "required": ["subject_id"]
            },
        ),
        types.Tool(
            name="get_my_episode_collections",
            description="获取当前用户剧集收藏信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "params": {
                        "type": "object",
                        "description": "可选参数，包含以下字段：",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "返回结果数量限制，默认30",
                                "default": 30
                            },
                            "offset": {
                                "type": "integer",
                                "description": "分页偏移量，默认0",
                                "default": 0
                            },
                            "episode_type": {
                                "type": "integer",
                                "description": "集数类型：0=本篇，1=特别篇，2=OP, 3=ED，4=预告/宣传/广告，5=MAD，6=其他",
                                "default": None
                            }
                        },
                        "default": {}
                    }
                },
                "required": ["subject_id"]
            }
        ),
        types.Tool(
            name="patch_my_episode_collections",
            description="为当前用户批量更改剧集收藏状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "episode_id": {
                        "type": "array",
                        "description": "剧集ID列表",
                        "items": {
                            "type": "integer"
                        }
                    },
                    "type": {
                        "type": "integer",
                        "description": "收藏类型：0=未收藏，1=想看，2=看过，3=抛弃",
                    },
                },
                "required": ["subject_id", "episode_id", "type"]
            }
        ),
        types.Tool(
            name="get_my_episode_collection_info",
            description="获取当前用户指定剧集收藏条目",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject_id": {
                        "type": "integer",
                        "description": "条目ID"
                    },
                    "episode_id": {
                        "type": "integer",
                        "description": "剧集ID"
                    }
                },
                "required": ["subject_id", "episode_id"]
            }
        ),
        types.Tool(
            name="put_my_episode_collection_info",
            description="为当前用户更改剧集收藏状态",
            inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {
                        "type": "integer",
                        "description": "剧集ID"
                    },
                    "type": {
                        "type": "integer",
                        "description": "收藏类型：0=未收藏，1=想看，2=看过，3=抛弃",
                    },
                },
                "required": [ "episode_id", "type"]
            }
        ),
        types.Tool(
            name="get_user_character_collections",
            description="获取用户角色收藏信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_user_character_collection_info",
            description="获取用户指定角色收藏信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                    "character_id": {
                        "type": "integer",
                        "description": "角色ID"
                    }
                },
                "required": ["username", "character_id"]
            }
        ),
        types.Tool(
            name="get_user_person_collections",
            description="获取用户人物收藏信息列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                },
                "required": ["username"]
            }
        ),
        types.Tool(
            name="get_user_person_collection_info",
            description="获取用户指定人物收藏信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户名/ID"
                    },
                    "person_id": {
                        "type": "integer",
                        "description": "人物ID"
                    }
                },
                "required": ["username", "person_id"]
            }
        ),
    ]
"""Pydantic models describing Bangumi API payloads.

The models are intentionally forgiving: Bangumi responses are generated from
an OpenAPI document that marks many nullable fields as required, and the API
also returns fields that the document does not describe. Every model therefore
permits extra keys (``extra="allow"``) so a schema refresh never drops data.

Tool return types are built from these models; the MCP SDK turns them into
``outputSchema`` definitions and validates ``structuredContent`` against them.
"""

from __future__ import annotations

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_serializer


class BangumiModel(BaseModel):
    """Base model that keeps unknown fields returned by the API."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_serializer(mode="wrap")
    def _drop_nulls(self, handler: Any) -> Any:
        """Omit ``null`` values so tool output stays compact.

        Bangumi marks many nullable fields as required. Keeping the fields in
        the JSON Schema (as nullable) while dropping them from the payload
        gives clients the best of both worlds.
        """
        data = handler(self)
        if isinstance(data, dict):
            return {key: value for key, value in data.items() if value is not None}
        return data


# ---------------------------------------------------------------------------
# shared building blocks
# ---------------------------------------------------------------------------
class Images(BangumiModel):
    large: str | None = None
    common: str | None = None
    medium: str | None = None
    small: str | None = None
    grid: str | None = None


class Avatar(BangumiModel):
    large: str | None = None
    medium: str | None = None
    small: str | None = None


class Tag(BangumiModel):
    name: str
    count: int | None = None
    total_count: int | None = None


class Rating(BangumiModel):
    rank: int | None = None
    total: int | None = None
    count: dict[str, int] | None = None
    score: float | None = None


class CollectionStat(BangumiModel):
    wish: int | None = None
    collect: int | None = None
    doing: int | None = None
    on_hold: int | None = None
    dropped: int | None = None


class Stat(BangumiModel):
    comments: int | None = None
    collects: int | None = None


class Creator(BangumiModel):
    username: str | None = None
    nickname: str | None = None


class Weekday(BangumiModel):
    en: str | None = None
    zh: str | None = None
    ja: str | None = None
    id: int | None = None


T = TypeVar("T")


class Page(BangumiModel, Generic[T]):
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[T] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# subjects
# ---------------------------------------------------------------------------
class Subject(BangumiModel):
    id: int
    type: int | None = None
    name: str | None = None
    name_cn: str | None = None
    summary: str | None = None
    date: str | None = None
    platform: str | None = None
    nsfw: bool | None = None
    locked: bool | None = None
    series: bool | None = None
    volumes: int | None = None
    eps: int | None = None
    total_episodes: int | None = None
    meta_tags: list[str] | None = None
    images: Images | None = None
    infobox: list[dict[str, Any]] | None = None
    rating: Rating | None = None
    collection: CollectionStat | None = None
    tags: list[Tag] | None = None


class SlimSubject(BangumiModel):
    id: int
    type: int | None = None
    name: str | None = None
    name_cn: str | None = None
    short_summary: str | None = None
    date: str | None = None
    images: Images | None = None
    volumes: int | None = None
    eps: int | None = None
    collection_total: int | None = None
    score: float | None = None
    rank: int | None = None
    tags: list[Tag] | None = None


class SubjectRelation(BangumiModel):
    id: int | None = None
    type: int | None = None
    name: str | None = None
    name_cn: str | None = None
    images: Images | None = None
    relation: str | None = None


class RelatedSubject(BangumiModel):
    id: int
    type: int | None = None
    staff: str | None = None
    eps: str | None = None
    name: str | None = None
    name_cn: str | None = None
    image: str | None = None


# ---------------------------------------------------------------------------
# characters & persons
# ---------------------------------------------------------------------------
class Character(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    images: Images | None = None
    summary: str | None = None
    locked: bool | None = None
    infobox: list[dict[str, Any]] | None = None
    gender: str | None = None
    blood_type: int | None = None
    birth_year: int | None = None
    birth_mon: int | None = None
    birth_day: int | None = None
    stat: Stat | None = None


class RelatedCharacter(BangumiModel):
    id: int
    name: str | None = None
    summary: str | None = None
    type: int | None = None
    images: Images | None = None
    relation: str | None = None
    actors: list["Person"] | None = None


class Person(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    career: list[str] | None = None
    images: Images | None = None
    short_summary: str | None = None
    locked: bool | None = None


class PersonDetail(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    career: list[str] | None = None
    images: Images | None = None
    summary: str | None = None
    short_summary: str | None = None
    locked: bool | None = None
    last_modified: str | None = None
    infobox: list[dict[str, Any]] | None = None
    gender: str | None = None
    blood_type: int | None = None
    birth_year: int | None = None
    birth_mon: int | None = None
    birth_day: int | None = None
    stat: Stat | None = None


class RelatedPerson(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    career: list[str] | None = None
    images: Images | None = None
    relation: str | None = None
    eps: str | None = None


class CharacterPerson(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    images: Images | None = None
    subject_id: int | None = None
    subject_type: int | None = None
    subject_name: str | None = None
    subject_name_cn: str | None = None
    staff: str | None = None


class PersonCharacter(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    images: Images | None = None
    subject_id: int | None = None
    subject_type: int | None = None
    subject_name: str | None = None
    subject_name_cn: str | None = None
    staff: str | None = None


# ---------------------------------------------------------------------------
# episodes
# ---------------------------------------------------------------------------
class Episode(BangumiModel):
    id: int
    type: int | None = None
    name: str | None = None
    name_cn: str | None = None
    sort: float | None = None
    ep: float | None = None
    airdate: str | None = None
    comment: int | None = None
    duration: str | None = None
    desc: str | None = None
    disc: int | None = None
    duration_seconds: int | None = None
    subject_id: int | None = None


class EpisodeDetail(Episode):
    subject_id: int | None = None


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------
class User(BangumiModel):
    id: int
    username: str | None = None
    nickname: str | None = None
    user_group: int | None = None
    avatar: Avatar | None = None
    sign: str | None = None
    url: str | None = None


# ---------------------------------------------------------------------------
# collections
# ---------------------------------------------------------------------------
class UserSubjectCollection(BangumiModel):
    subject_id: int
    subject_type: int | None = None
    rate: int | None = None
    type: int | None = None
    comment: str | None = None
    tags: list[str] | None = None
    ep_status: int | None = None
    vol_status: int | None = None
    updated_at: str | None = None
    private: bool | None = None
    subject: SlimSubject | None = None


class UserEpisodeCollection(BangumiModel):
    episode: Episode | None = None
    type: int | None = None
    updated_at: int | None = None


class UserCharacterCollection(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    images: Images | None = None
    created_at: str | None = None


class UserPersonCollection(BangumiModel):
    id: int
    name: str | None = None
    type: int | None = None
    career: list[str] | None = None
    images: Images | None = None
    created_at: str | None = None


# ---------------------------------------------------------------------------
# revisions
# ---------------------------------------------------------------------------
class Revision(BangumiModel):
    id: int
    type: int | None = None
    creator: Creator | None = None
    summary: str | None = None
    created_at: str | None = None


# ---------------------------------------------------------------------------
# indices
# ---------------------------------------------------------------------------
class Index(BangumiModel):
    id: int
    title: str | None = None
    desc: str | None = None
    total: int | None = None
    stat: Stat | None = None
    created_at: str | None = None
    updated_at: str | None = None
    creator: Creator | None = None
    ban: bool | None = None
    nsfw: bool | None = None


class IndexSubject(BangumiModel):
    id: int
    type: int | None = None
    name: str | None = None
    images: Images | None = None
    infobox: list[dict[str, Any]] | None = None
    date: str | None = None
    comment: str | None = None
    added_at: str | None = None


# ---------------------------------------------------------------------------
# calendar
# ---------------------------------------------------------------------------
class LegacySubject(BangumiModel):
    id: int
    url: str | None = None
    type: int | None = None
    name: str | None = None
    name_cn: str | None = None
    summary: str | None = None
    air_date: str | None = None
    air_weekday: int | None = None
    images: Images | None = None
    eps: int | None = None
    eps_count: int | None = None
    rating: Rating | None = None
    rank: int | None = None
    collection: CollectionStat | None = None


class CalendarDay(BangumiModel):
    weekday: Weekday | None = None
    items: list[LegacySubject] = Field(default_factory=list)


class CalendarOutput(BangumiModel):
    calendar: list[CalendarDay] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# tool results
# ---------------------------------------------------------------------------
class SubjectSearchResult(BangumiModel):
    entity: Literal["subject"] = "subject"
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[Subject] = Field(default_factory=list)


class CharacterSearchResult(BangumiModel):
    entity: Literal["character"] = "character"
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[Character] = Field(default_factory=list)


class PersonSearchResult(BangumiModel):
    entity: Literal["person"] = "person"
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[Person] = Field(default_factory=list)


SearchResult = SubjectSearchResult | CharacterSearchResult | PersonSearchResult


class SubjectDetail(BangumiModel):
    subject: Subject
    characters: list[RelatedCharacter] | None = None
    persons: list[RelatedPerson] | None = None
    relations: list[SubjectRelation] | None = None
    episodes: list[Episode] | None = None


class EntityDetail(BangumiModel):
    entity_type: Literal["character", "person"]
    character: Character | None = None
    person: PersonDetail | None = None
    subjects: list[SubjectRelation] | None = None
    related_persons: list[CharacterPerson] | None = None
    related_characters: list[PersonCharacter] | None = None


class EpisodeResult(BangumiModel):
    episode: EpisodeDetail | None = None
    total: int = 0
    limit: int = 0
    offset: int = 0
    data: list[Episode] = Field(default_factory=list)


class RevisionsResult(BangumiModel):
    entity: Literal["subject", "episode", "character", "person"]
    revision: dict[str, Any] | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    data: list[Revision] = Field(default_factory=list)


class SubjectCollectionsResult(BangumiModel):
    resource: Literal["subject"] = "subject"
    collection: UserSubjectCollection | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    data: list[UserSubjectCollection] = Field(default_factory=list)


class EpisodeCollectionsResult(BangumiModel):
    resource: Literal["episode"] = "episode"
    collection: UserEpisodeCollection | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    data: list[UserEpisodeCollection] = Field(default_factory=list)


class CharacterCollectionsResult(BangumiModel):
    resource: Literal["character"] = "character"
    collection: UserCharacterCollection | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    data: list[UserCharacterCollection] = Field(default_factory=list)


class PersonCollectionsResult(BangumiModel):
    resource: Literal["person"] = "person"
    collection: UserPersonCollection | None = None
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    data: list[UserPersonCollection] = Field(default_factory=list)


CollectionsResult = (
    SubjectCollectionsResult
    | EpisodeCollectionsResult
    | CharacterCollectionsResult
    | PersonCollectionsResult
)


class WriteResult(BangumiModel):
    ok: bool = True
    resource: str
    action: str
    ids: list[int] = Field(default_factory=list)
    message: str


class IndexActionResult(BangumiModel):
    action: str
    ok: bool = True
    message: str
    index: Index | None = None
    subjects: Page[IndexSubject] | None = None


# Resolve the forward references used by RelatedCharacter.actors.
RelatedCharacter.model_rebuild()

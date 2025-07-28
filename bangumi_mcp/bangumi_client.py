"""Bangumi API client for interacting with the Bangumi API."""

import os
from typing import Any, Dict, List, Optional, Union
import httpx
from dotenv import load_dotenv


class BangumiClient:
    """Client for interacting with the Bangumi API."""
    
    BASE_URL = "https://api.bgm.tv"
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the Bangumi client.
        
        Args:
            token: Bangumi API token. If not provided, will try to load from .env file.
        """
        load_dotenv()
        self.token = token or os.getenv("BANGUMI_API_TOKEN")
        if not self.token:
            self.token = None
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "User-Agent": "https://github.com/etherwindy/Bangumi-MCP",
                "Content-Type": "application/json",
                "accept": "*/*",
            }
        )
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def get_calendar(self) -> tuple[int, Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Get calendar information (currently airing anime).
        """
        response = await self.client.get("/calendar")
        
        return response.status_code, response.json()

    async def search_subjects(self, params) -> tuple[int, Dict[str, Any]]:
        """Search for subjects (anime, manga, etc.).

        Args:
            params: Search parameters including keyword, type, limit, etc.
        Returns:
            Search results as a dictionary.
        """

        response = await self.client.post("/v0/search/subjects", json=params)
        
        return response.status_code, response.json()

    async def get_subjects(self, params) -> tuple[int, Dict[str, Any]]:
        """Browse subjects (anime, manga, etc.).

        Args:
            params: Parameters for filtering subjects, including type, category, series, platform, sort,
            limit, and offset.
        Returns:
            List of subjects matching the criteria.
        """
        response = await self.client.get("/v0/subjects", params=params)
        
        return response.status_code, response.json()

    async def get_subject_info(self, subject_id: int) -> tuple[int, Dict[str, Any]]:
        """Get detailed information about a subject.
        
        Args:
            subject_id: Subject ID
        Returns:
            Subject information
        """
        response = await self.client.get(f"/v0/subjects/{subject_id}")
        
        return response.status_code, response.json()

    async def get_subject_image(self, subject_id: int, params: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """Get images for a subject.
        
        Args:
            subject_id: Subject ID
        Returns:
            List of images for the subject
        """
        response = await self.client.get(f"/v0/subjects/{subject_id}/image", params=params)
        # get header for image URLs
        if response.status_code == 302:
            url = response.headers.get("Location", "")
            return response.status_code, {"url": url}
        else:
            
            return response.status_code, response.json()

    async def get_subject_persons(self, subject_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Get persons (staff) for a subject.
        
        Args:
            subject_id: Subject ID
        Returns:
            List of persons/staff
        """
        response = await self.client.get(f"/v0/subjects/{subject_id}/persons")
        
        return response.status_code, response.json()

    async def get_subject_characters(self, subject_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Get characters for a subject.
        
        Args:
            subject_id: Subject ID
        Returns:
            List of characters
        """
        response = await self.client.get(f"/v0/subjects/{subject_id}/characters")
        
        return response.status_code, response.json()

    async def get_subject_relations(self, subject_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Get related subjects for a subject.
        
        Args:
            subject_id: Subject ID
        Returns:
            List of related subjects
        """
        response = await self.client.get(f"/v0/subjects/{subject_id}/subjects")
        
        return response.status_code, response.json()

    async def get_episodes(self, params) -> tuple[int, Dict[str, Any]]:
        """Get episodes for a subject.

        Args:
            params: Parameters including subject_id and episode_type.
        Returns:
            List of episodes for the subject.
        """
        response = await self.client.get(f"/v0/episodes", params=params)
        
        return response.status_code, response.json()

    async def get_episode_info(self, episode_id: int) -> tuple[int, Dict[str, Any]]:
        """Get detailed information about an episode.
        
        Args:
            episode_id: Episode ID
        Returns:
            Episode information
        """
        response = await self.client.get(f"/v0/episodes/{episode_id}")
        
        return response.status_code, response.json()

    async def search_characters(self, params) -> tuple[int, Dict[str, Any]]:
        """Search for characters.
        
        Args:
            params: Search parameters including keyword, limit, and offset.
        Returns:
            Search results as a dictionary.
        """
        response = await self.client.post("/v0/search/characters", json=params)
        
        return response.status_code, response.json()

    async def get_character_info(self, character_id: int) -> tuple[int, Dict[str, Any]]:
        """Get character information.
        
        Args:
            character_id: Character ID
        Returns:
            Character information
        """
        response = await self.client.get(f"/v0/characters/{character_id}")
        
        return response.status_code, response.json()

    async def get_character_subjects(self, character_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """
        Get subjects related to a character.
        
        Args:
            character_id: Character ID
        Returns:
            List of related subjects
        """
        response = await self.client.get(f"/v0/characters/{character_id}/subjects")
        
        return response.status_code, response.json()

    async def get_character_persons(self, character_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """
        Get persons related to a character.
        
        Args:
            character_id: Character ID
        Returns:
            List of related persons
        """
        response = await self.client.get(f"/v0/characters/{character_id}/persons")
        
        return response.status_code, response.json()

    async def post_character_collection(self, character_id: int) -> tuple[int, Dict[str, Any]]:
        """Collect a character.

        Args:
            character_id: Character ID
        Returns:
            Collection result
        """
        response = await self.client.post(f"/v0/characters/{character_id}/collect")
        

        status_code = response.status_code
        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def delete_character_collection(self, character_id: int) -> tuple[int, Dict[str, Any]]:
        """Uncollect a character.

        Args:
            character_id: Character ID
        Returns:
            Uncollection result
        """
        response = await self.client.delete(f"/v0/characters/{character_id}/collect")
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def search_persons(self, params) -> tuple[int, Dict[str, Any]]:
        """Search for persons (staff).
        
        Args:
            params: Search parameters including keyword, limit, and offset.
        Returns:
            Search results as a dictionary.
        """
        response = await self.client.post("/v0/search/persons", json=params)
        
        return response.status_code, response.json()
    
    async def get_person_info(self, person_id: int) -> tuple[int, Dict[str, Any]]:
        """Get detailed information about a person.
        
        Args:
            person_id: Person ID
        Returns:
            Person information
        """
        response = await self.client.get(f"/v0/persons/{person_id}")
        
        return response.status_code, response.json()

    async def get_person_subjects(self, person_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Get subjects related to a person.
        
        Args:
            person_id: Person ID
        Returns:
            List of related subjects
        """
        response = await self.client.get(f"/v0/persons/{person_id}/subjects")
        
        return response.status_code, response.json()

    async def get_person_characters(self, person_id: int) -> tuple[int, Union[List[Dict[str, Any]], Dict[str, Any]]]:
        """Get characters related to a person.
        
        Args:
            person_id: Person ID
        Returns:
            List of related characters
        """
        response = await self.client.get(f"/v0/persons/{person_id}/characters")
        
        return response.status_code, response.json()
    
    async def post_person_collection(self, person_id: int) -> tuple[int, Dict[str, Any]]:
        """Collect a person.
        
        Args:
            person_id: Person ID
        Returns:
            Collection result
        """
        response = await self.client.post(f"/v0/persons/{person_id}/collect")
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def delete_person_collection(self, person_id: int) -> tuple[int, Dict[str, Any]]:
        """Uncollect a person.
        
        Args:
            person_id: Person ID
        Returns:
            Uncollection result
        """
        response = await self.client.delete(f"/v0/persons/{person_id}/collect")
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def get_user_info(self, username: str) -> tuple[int, Dict[str, Any]]:
        """Get user information by username."""
        response = await self.client.get(f"/v0/users/{username}")
        
        return response.status_code, response.json()
    
    async def get_me_info(self) -> tuple[int, Dict[str, Any]]:
        """Get current user's information."""
        response = await self.client.get("/v0/me")
        
        return response.status_code, response.json()

    async def get_user_collections(
        self, 
        username: str,
        params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's collection.
        
        Args:
            username: Username (if None, get current user's collection)
            subject_type: Subject type filter
            limit: Number of results to return
            offset: Offset for pagination
        Returns:
            User collection
        """
        if username:
            url = f"/v0/users/{username}/collections"
        else:
            raise ValueError("Username must be provided to get collections")

        response = await self.client.get(url, params=params)
        
        return response.status_code, response.json()

    async def get_user_collection_info(
        self, 
        username: str, 
        subject_id: int
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's collection info for a specific subject.
        
        Args:
            username: Username
            subject_id: Subject ID
        Returns:
            User's collection info for the subject
        """
        response = await self.client.get(f"/v0/users/{username}/collections/{subject_id}")
        
        return response.status_code, response.json()

    async def post_my_collection(
        self, 
        subject_id: int, 
        params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Dict[str, Any]]:
        """Collect a subject for the current user.
        
        Args:
            subject_id: Subject ID
            params: Parameters for collecting the subject
        Returns:
            Collection result
        """
        response = await self.client.post(f"/v0/users/-/collections/{subject_id}", json=params)
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    
    async def patch_my_collection(
        self, 
        subject_id: int, 
        params: Dict[str, Any]
    ) -> tuple[int, Dict[str, Any]]:
        """Patch user's collection for a subject.
        
        Args:
            subject_id: Subject ID
            params: Parameters for patching the collection
        Returns:
            Updated collection info
        """
        response = await self.client.patch(f"/v0/users/-/collections/{subject_id}", json=params)
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    
    async def get_my_episode_collections(
        self, 
        subject_id: int,
        params: Optional[Dict[str, Any]] = None
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's episode collections.
        
        Args:
            username: Username (if None, get current user's episode collections)
            params: Additional parameters for filtering
        Returns:
            User's episode collections
        """
        if subject_id:
            url = f"/v0/users/-/collections/{subject_id}/episodes"
        else:
            raise ValueError("Username must be provided to get episode collections")

        response = await self.client.get(url, params=params)
        
        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def patch_my_episode_collections(
        self, 
        subject_id: int, 
        params: Dict[str, Any]
    ) -> tuple[int, Dict[str, Any]]:
        """Patch user's episode collection.
        
        Args:
            subject_id: Subject ID
            params: Parameters for patching the collection
        Returns:
            Updated episode collection info
        """
        response = await self.client.patch(f"/v0/users/-/collections/{subject_id}/episodes", json=params)
        
        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()
    
    async def get_my_episode_collection_info(
        self, 
        episode_id: int
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's episode collection info for a specific episode.
        
        Args:
            episode_id: Episode ID
        Returns:
            User's episode collection info for the episode
        """
        response = await self.client.get(f"/v0/users/-/collections/-/episodes/{episode_id}")
        
        return response.status_code, response.json()
    
    async def put_my_episode_collection_info(
        self, 
        episode_id: int, 
        params: Dict[str, Any]
    ) -> tuple[int, Dict[str, Any]]:
        """Update user's episode collection.
        
        Args:
            episode_id: Episode ID
            params: Parameters for updating the collection
        Returns:
            Updated episode collection info
        """
        response = await self.client.put(f"/v0/users/-/collections/-/episodes/{episode_id}", json=params)
        

        if response.content == b'':
            return response.status_code, {}
        else:
            return response.status_code, response.json()

    async def get_user_character_collections(self, username: str) -> tuple[int, Dict[str, Any]]:
        """Get user's character collections.
        
        Args:
            username: Username
        Returns:
            User's character collections
        """
        if username:
            url = f"/v0/users/{username}/collections/-/characters"
        else:
            raise ValueError("Username must be provided to get character collections")

        response = await self.client.get(url)
        
        return response.status_code, response.json()
    
    async def get_user_character_collection_info(
        self, 
        username: str, 
        character_id: int
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's character collection info for a specific character.
        
        Args:
            username: Username
            character_id: Character ID
        Returns:
            User's character collection info for the character
        """
        response = await self.client.get(f"/v0/users/{username}/collections/-/characters/{character_id}")
        
        return response.status_code, response.json()
    
    async def get_user_person_collections(self, username: str) -> tuple[int, Dict[str, Any]]:
        """Get user's person collections.
        
        Args:
            username: Username
        Returns:
            User's person collections
        """
        if username:
            url = f"/v0/users/{username}/collections/-/persons"
        else:
            raise ValueError("Username must be provided to get person collections")

        response = await self.client.get(url)
        
        return response.status_code, response.json()
    
    async def get_user_person_collection_info(
        self, 
        username: str, 
        person_id: int
    ) -> tuple[int, Dict[str, Any]]:
        """Get user's person collection info for a specific person.
        
        Args:
            username: Username
            person_id: Person ID
        Returns:
            User's person collection info for the person
        """
        response = await self.client.get(f"/v0/users/{username}/collections/-/persons/{person_id}")
        
        return response.status_code, response.json()
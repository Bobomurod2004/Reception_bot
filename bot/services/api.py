import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    DJANGO_API_URL, API_TOKEN, API_TIMEOUT, 
    API_MAX_RETRIES, API_RETRY_DELAY
)

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    """Django backend bilan bog'lanish uchun API client (optimized with session reuse)"""
    
    def __init__(self):
        self.base_url = DJANGO_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN}'
        }
        self._session: Optional[aiohttp.ClientSession] = None
        self._timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
        self._connector: Optional[aiohttp.TCPConnector] = None
    
    def _get_connector(self) -> aiohttp.TCPConnector:
        """Get or create TCPConnector (lazy initialization to avoid event loop issues)"""
        if self._connector is None or self._connector.closed:
            self._connector = aiohttp.TCPConnector(
                limit=100,  # Max connections
                limit_per_host=30,  # Max connections per host
                ttl_dns_cache=300,  # DNS cache TTL
                force_close=False,  # Reuse connections
            )
        return self._connector
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session (reused for all requests)"""
        if self._session is None or self._session.closed:
            connector = self._get_connector()
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=self._timeout,
                connector=connector,
                json_serialize=lambda x: __import__('json').dumps(x, ensure_ascii=False)
            )
        return self._session
    
    async def close(self):
        """Close the session and connector (call on shutdown)"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("API client session closed")
        if self._connector and not self._connector.closed:
            await self._connector.close()
            logger.info("API client connector closed")
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        max_retries: int = None,
        retry_delay: float = None
    ) -> Optional[Dict]:
        """HTTP so'rov yuborish (retry strategy bilan, optimized session reuse)"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        max_retries = max_retries or API_MAX_RETRIES
        retry_delay = retry_delay or API_RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                session = await self._get_session()
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=self.headers,
                ) as response:
                        if response.status == 204:  # No Content
                            return {}
                        
                        try:
                            response_data = await response.json()
                        except Exception as json_error:
                            logger.error(f"JSON parse error for {url}: {json_error}")
                            text = await response.text()
                            logger.error(f"Response text: {text[:200]}")
                            # Retry qilish (server xatosi)
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (attempt + 1))
                                continue
                            return None
                        
                        if response.status >= 500:
                            # Server xatosi - retry qilish
                            logger.warning(f"Server error {response.status} for {url}, attempt {attempt + 1}/{max_retries}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay * (attempt + 1))
                                continue
                            return None
                        
                        if response.status >= 400:
                            # Client xatosi - retry qilmaslik
                            logger.error(
                                f"API Error {response.status} for {method} {url}: {response_data}"
                            )
                            return None
                        
                        logger.debug(f"API Response for {url}: {response_data}")
                        return response_data
                        
            except aiohttp.ClientError as e:
                logger.warning(f"API Client Error for {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return None
            except asyncio.TimeoutError:
                logger.warning(f"API Timeout for {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {e}", exc_info=True)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return None
        
        logger.error(f"Max retries ({max_retries}) reached for {url}")
        return None
    
    # User API methods
    async def create_user(self, telegram_id: int, username: str = None, 
                         first_name: str = None, last_name: str = None) -> Optional[Dict]:
        """User yaratish"""
        data = {
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        return await self._make_request('POST', 'user/users/', data)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Telegram ID bo'yicha user topish (filtr bilan)"""
        params = {'telegram_id': telegram_id}
        response = await self._make_request('GET', 'user/users/', params=params)
        
        if response and isinstance(response, dict):
            results = response.get('results', [])
            if results:
                return results[0]
        elif isinstance(response, list) and response:
            return response[0]
            
        return None
    
    async def get_user_tickets(self, user_id: int) -> Optional[List[Dict]]:
        """User ticketlarini olish (pagination bilan)"""
        all_tickets = []
        url = 'ticket/tickets/user-tickets/'
        params = {'user_id': user_id}
        
        while url:
            response = await self._make_request('GET', url, params=params)
            if not response:
                break
                
            if isinstance(response, dict):
                tickets = response.get('results', [])
                all_tickets.extend(tickets)
                
                next_url = response.get('next')
                if next_url:
                    url = next_url.replace(self.base_url + '/', '') if self.base_url in next_url else next_url
                    params = None  # Next URL-da params allaqachon bor
                else:
                    url = None
            elif isinstance(response, list):
                all_tickets.extend(response)
                url = None
            else:
                break
                
        return all_tickets
    
    # Category API methods
    async def get_categories(self, lang='uz') -> Optional[List[Dict]]:
        """Get categories with language support"""
        all_categories = []
        url = f'admin/categories/?lang={lang}'
        
        while url:
            response = await self._make_request('GET', url)
            if not response:
                break
                
            if isinstance(response, dict):
                categories = response.get('results', [])
                all_categories.extend(categories)
                
                next_url = response.get('next')
                if next_url:
                    url = next_url.replace(self.base_url + '/', '') if self.base_url in next_url else next_url
                else:
                    url = None
            elif isinstance(response, list):
                all_categories.extend(response)
                url = None
            else:
                break
                
        return all_categories
    
    async def get_category(self, category_id: int) -> Optional[Dict]:
        """Bitta kategoriya olish"""
        return await self._make_request('GET', f'admin/categories/{category_id}/')
    
    # Ticket API methods
    async def create_ticket(self, user_id: int, title: str, category_id: int, 
                           description: str, priority: str = 'medium') -> Optional[Dict]:
        """Ticket yaratish"""
        data = {
            'user': user_id,
            'title': title,
            'category': category_id,
            'description': description,
            'priority': priority
        }
        return await self._make_request('POST', 'ticket/tickets/', data)
    
    async def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Bitta ticket olish"""
        return await self._make_request('GET', f'ticket/tickets/{ticket_id}/')
    
    async def update_ticket_status(self, ticket_id: int, status: str) -> Optional[Dict]:
        """Ticket statusini yangilash"""
        data = {'status': status}
        return await self._make_request('PATCH', f'ticket/tickets/{ticket_id}/', data)
    
    async def close_ticket(self, ticket_id: int, admin_id: int = None, 
                          close_reason: str = '') -> Optional[Dict]:
        """Ticketni yopish"""
        data = {
            'close_reason': close_reason,
            'admin_id': admin_id
        }
        return await self._make_request('POST', f'ticket/tickets/{ticket_id}/close/', data)
    
    async def close_expired_tickets(self) -> Optional[Dict]:
        """Auto-close expired tickets"""
        return await self._make_request('POST', 'ticket/tickets/close_expired/')

    # Message API methods
    async def create_message(self, ticket_id: int, sender_user_id: int = None,
                           sender_admin_id: int = None, content_type: str = 'text',
                           content: str = None, file_id: str = None) -> Optional[Dict]:
        """Message yaratish"""
        data = {
            'ticket': ticket_id,
            'content_type': content_type,
            'content': content
        }
        
        if sender_user_id:
            data['sender_user'] = sender_user_id
        elif sender_admin_id:
            data['sender_admin'] = sender_admin_id
            
        if file_id:
            data['file'] = file_id
            
        return await self._make_request('POST', 'ticket/messages/', data)
    
    async def get_ticket_messages(self, ticket_id: int) -> Optional[List[Dict]]:
        """Ticket xabarlarini olish (filtr bilan)"""
        all_messages = []
        url = 'ticket/messages/'
        params = {'ticket': ticket_id}
        
        while url:
            response = await self._make_request('GET', url, params=params)
            if not response:
                break
                
            if isinstance(response, dict):
                messages = response.get('results', [])
                all_messages.extend(messages)
                next_url = response.get('next')
                if next_url:
                    url = next_url.replace(self.base_url + '/', '') if self.base_url in next_url else next_url
                    params = None
                else:
                    url = None
            elif isinstance(response, list):
                all_messages.extend(response)
                url = None
            else:
                break
        
        return all_messages
    
    # Admin API methods
    async def get_admin_by_user_id(self, user_id: int) -> Optional[Dict]:
        """User ID bo'yicha admin topish (filtr bilan)"""
        params = {'user_id': user_id}
        response = await self._make_request('GET', 'admin/admins/', params=params)
        
        if response and isinstance(response, dict):
            results = response.get('results', [])
            if results:
                return results[0]
        elif isinstance(response, list) and response:
            return response[0]
            
        return None
    
    async def get_admin_tickets(self, admin_id: int, date_filter: str = 'today') -> Optional[List[Dict]]:
        """Admin ticketlarini olish (pagination va filtr bilan)"""
        all_tickets = []
        url = 'ticket/tickets/my-tickets/'
        params = {'admin_id': admin_id, 'date_filter': date_filter}
        
        while url:
            response = await self._make_request('GET', url, params=params)
            if not response:
                break
                
            if isinstance(response, dict):
                tickets = response.get('results', [])
                all_tickets.extend(tickets)
                
                next_url = response.get('next')
                if next_url:
                    url = next_url.replace(self.base_url + '/', '') if self.base_url in next_url else next_url
                    params = None
                else:
                    url = None
            elif isinstance(response, list):
                all_tickets.extend(response)
                url = None
            else:
                break
                
        return all_tickets
    
    async def assign_admin_to_ticket(self, ticket_id: int, admin_id: int) -> Optional[Dict]:
        """Ticketga admin biriktirish"""
        data = {'admin_id': admin_id}
        return await self._make_request('POST', f'ticket/tickets/{ticket_id}/assign-admin/', data)


# Global API client instance
api_client = DjangoAPIClient()

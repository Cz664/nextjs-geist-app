from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
from datetime import datetime
from PIL import Image
import os
import logging
import requests
import json
import asyncio
from pydantic import BaseModel
import aiohttp
import re
from urllib.parse import quote, unquote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_CONFIG = {
    "licenselookup": {
        "url": "https://api.licenselookup.org/usa-advanced-phone-search",
        "token": "c075331473726f1395e915ec7d1bb67c"
    },
    "rapidapi": {
        "key": "a9c563c006msh330f7a2f874b43ep1a9cb8jsn52d5c04e38cc",
        "osint": {
            "url": "https://osint-phone-email-names-search-everything.p.rapidapi.com/search",
            "host": "osint-phone-email-names-search-everything.p.rapidapi.com"
        }
    }
}

# Target platforms list
TARGET_PLATFORMS = [
    "Facebook", "Instagram", "Twitter/X", "LinkedIn", "TikTok", "YouTube",
    "Snapchat", "Reddit", "Discord", "Telegram", "WhatsApp",
    "Cash App", "Venmo", "PayPal", "Zelle", "Apple Pay", "Google Pay", "Amazon Pay",
    "Google Store", "Coinbase", "Crypto.com", "Kraken", "Charles Schwab",
    "E*TRADE", "TD Ameritrade", "Webull", "Robinhood"
]

# Initialize FastAPI app
app = FastAPI(
    title="深度挖掘系统",
    description="12步骤手机号码深度挖掘和网站信息提取"
)

# Add CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
API_CONFIG = {
    "licenselookup": {
        "url": "https://api.licenselookup.org/usa-advanced-phone-search",
        "token": "c075331473726f1395e915ec7d1bb67c"
    },
    "rapidapi": {
        "key": "a9c563c006msh330f7a2f874b43ep1a9cb8jsn52d5c04e38cc",
        "osint": {
            "url": "https://osint-phone-email-names-search-everything.p.rapidapi.com/search",
            "host": "osint-phone-email-names-search-everything.p.rapidapi.com"
        },
        "zillow": {
            "host": "the-best-zillow-scraper-api.p.rapidapi.com",
            "property_detail": "https://the-best-zillow-scraper-api.p.rapidapi.com/api/v1/property/detail",
            "agent_zuid": "https://the-best-zillow-scraper-api.p.rapidapi.com/api/v1/agent/zuid",
            "legal_protection": "https://the-best-zillow-scraper-api.p.rapidapi.com/api/v1/property/local-legal-protection"
        },
        "whatsapp": {
            "host": "whatsapp-osint.p.rapidapi.com",
            "dck": "https://whatsapp-osint.p.rapidapi.com/wspic/dck",
            "b64": "https://whatsapp-osint.p.rapidapi.com/wspic/b64",
            "about": "https://whatsapp-osint.p.rapidapi.com/about"
        },
        "login": {
            "url": "https://sign-in-api.p.rapidapi.com/api/account/sign-up",
            "host": "sign-in-api.p.rapidapi.com"
        },
        "eyecon": {
            "host": "caller-id-social-search-eyecon.p.rapidapi.com",
            "social_search": "https://caller-id-social-search-eyecon.p.rapidapi.com/",
            "image_lookup": "https://caller-id-social-search-eyecon.p.rapidapi.com/image_lookup.php"
        },
        "website_contact": {
            "url": "https://website-contact-finder.p.rapidapi.com/",
            "host": "website-contact-finder.p.rapidapi.com"
        }
    }
}

# Target platforms list
TARGET_PLATFORMS = [
    "Facebook", "Instagram", "Twitter/X", "LinkedIn", "TikTok", "YouTube",
    "Snapchat", "Reddit", "Discord", "Telegram", "WhatsApp",
    "Cash App", "Venmo", "PayPal", "Zelle", "Apple Pay", "Google Pay", "Amazon Pay",
    "Google Store", "Coinbase", "Crypto.com", "Kraken", "Charles Schwab",
    "E*TRADE", "TD Ameritrade", "Webull", "Robinhood"
]

# Pydantic models
class PhoneSearchRequest(BaseModel):
    phone_number: str

class SearchResult(BaseModel):
    platform: str
    found: bool
    details: Optional[Dict[str, Any]] = None

class PhoneSearchResponse(BaseModel):
    phone_number: str
    basic_info: Dict[str, Any]
    social_media: List[SearchResult]
    financial: List[SearchResult]
    additional_info: Optional[Dict[str, Any]] = None
    timestamp: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class UserRole(BaseModel):
    role: str
    level: int
    permissions: List[str]
    commission_rate: float

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_info: Optional[Dict[str, Any]] = None
    token: Optional[str] = None

class DistributionStats(BaseModel):
    user_id: str
    role: str
    level: int
    total_searches: int
    total_earnings: float
    team_size: int
    direct_referrals: int
    commission_rate: float

# User database (in production, use a real database)
USERS_DB = {
    "boss": {
        "password": "boss123",
        "role": "BOSS",
        "level": 1,
        "permissions": ["all_access", "manage_users", "view_all_stats", "set_commission"],
        "commission_rate": 0.50,
        "user_id": "boss_001",
        "team_size": 100,
        "total_searches": 5000,
        "total_earnings": 25000.0,
        "direct_referrals": 10
    },
    "ceo": {
        "password": "ceo123",
        "role": "CEO",
        "level": 2,
        "permissions": ["manage_team", "view_team_stats", "recruit_users"],
        "commission_rate": 0.30,
        "user_id": "ceo_001",
        "team_size": 50,
        "total_searches": 2500,
        "total_earnings": 7500.0,
        "direct_referrals": 25
    },
    "yy": {
        "password": "yy123",
        "role": "YY",
        "level": 3,
        "permissions": ["basic_search", "view_own_stats"],
        "commission_rate": 0.10,
        "user_id": "yy_001",
        "team_size": 0,
        "total_searches": 500,
        "total_earnings": 500.0,
        "direct_referrals": 5
    },
    "admin": {
        "password": "password123",
        "role": "ADMIN",
        "level": 0,
        "permissions": ["all_access", "system_admin"],
        "commission_rate": 0.0,
        "user_id": "admin_001",
        "team_size": 0,
        "total_searches": 0,
        "total_earnings": 0.0,
        "direct_referrals": 0
    }
}

# Mount static files
app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("public/login.html")

@app.post("/api/login")
async def login(request: LoginRequest):
    username = request.username.lower()
    password = request.password
    
    if username in USERS_DB and USERS_DB[username]["password"] == password:
        user_data = USERS_DB[username]
        return LoginResponse(
            success=True,
            message="Login successful",
            user_info={
                "username": username,
                "role": user_data["role"],
                "level": user_data["level"],
                "permissions": user_data["permissions"],
                "commission_rate": user_data["commission_rate"]
            },
            token=f"token_{username}_{user_data['user_id']}"
        )
    else:
        return LoginResponse(
            success=False,
            message="Invalid credentials"
        )

@app.get("/api/dashboard/{username}")
async def get_dashboard(username: str):
    username = username.lower()
    if username not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = USERS_DB[username]
    return DistributionStats(
        user_id=user_data["user_id"],
        role=user_data["role"],
        level=user_data["level"],
        total_searches=user_data["total_searches"],
        total_earnings=user_data["total_earnings"],
        team_size=user_data["team_size"],
        direct_referrals=user_data["direct_referrals"],
        commission_rate=user_data["commission_rate"]
    )

@app.get("/api/team/{username}")
async def get_team_stats(username: str):
    username = username.lower()
    if username not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = USERS_DB[username]
    
    # Mock team data based on role
    if user_data["role"] == "BOSS":
        team_data = [
            {"username": "ceo_1", "role": "CEO", "searches": 1200, "earnings": 3600},
            {"username": "ceo_2", "role": "CEO", "searches": 800, "earnings": 2400},
            {"username": "ceo_3", "role": "CEO", "searches": 500, "earnings": 1500}
        ]
    elif user_data["role"] == "CEO":
        team_data = [
            {"username": "yy_1", "role": "YY", "searches": 200, "earnings": 200},
            {"username": "yy_2", "role": "YY", "searches": 150, "earnings": 150},
            {"username": "yy_3", "role": "YY", "searches": 100, "earnings": 100},
            {"username": "yy_4", "role": "YY", "searches": 50, "earnings": 50}
        ]
    else:
        team_data = []
    
    return {"team": team_data, "total_members": len(team_data)}
    phone = request.phone_number
    logger.info(f"Searching for phone number: {phone}")
    
    try:
        # Basic phone lookup using licenselookup API
        basic_info = await get_basic_phone_info(phone)
        
        # Parallel social media and financial platform searches
        social_results = []
        financial_results = []
        
        social_tasks = [check_social_platform(phone, platform) 
                       for platform in TARGET_PLATFORMS 
                       if platform not in ["Cash App", "Venmo", "PayPal", "Zelle", "Apple Pay", "Google Pay", "Amazon Pay",
                                        "Coinbase", "Crypto.com", "Kraken", "Charles Schwab", "E*TRADE", "TD Ameritrade", 
                                        "Webull", "Robinhood"]]
        
        financial_tasks = [check_financial_platform(phone, platform)
                          for platform in TARGET_PLATFORMS
                          if platform in ["Cash App", "Venmo", "PayPal", "Zelle", "Apple Pay", "Google Pay", "Amazon Pay",
                                        "Coinbase", "Crypto.com", "Kraken", "Charles Schwab", "E*TRADE", "TD Ameritrade",
                                        "Webull", "Robinhood"]]
        
        social_results = await asyncio.gather(*social_tasks)
        financial_results = await asyncio.gather(*financial_tasks)
        
        # Additional OSINT searches
        additional_info = await get_additional_info(phone)
        
        response = PhoneSearchResponse(
            phone_number=phone,
            basic_info=basic_info,
            social_media=social_results,
            financial=financial_results,
            additional_info=additional_info,
            timestamp=datetime.now()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing phone search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_basic_phone_info(phone: str) -> Dict[str, Any]:
    """Get mock basic phone information"""
    return {
        "phone_number": phone,
        "carrier": "CYBER MOBILE",
        "location": "NEO CITY, CA",
        "line_type": "MOBILE",
        "status": "ACTIVE",
        "risk_level": "LOW",
        "last_seen": "2077-06-22"
    }

async def check_social_platform(phone: str, platform: str) -> SearchResult:
    """Check if phone number is associated with a social media platform"""
    try:
        # Mock data for demonstration
        mock_data = {
            "Facebook": {
                "found": True,
                "username": "cyber.user",
                "last_active": "2077-06-21",
                "profile_image": "https://i.pravatar.cc/150?u=facebook_cyber_user"
            },
            "Instagram": {
                "found": True,
                "username": "@cyber_user",
                "followers": 1337,
                "profile_image": "https://i.pravatar.cc/150?u=instagram_cyber_user"
            },
            "Twitter/X": {
                "found": True,
                "handle": "@cyber_user",
                "verified": True,
                "profile_image": "https://i.pravatar.cc/150?u=twitter_cyber_user"
            },
            "LinkedIn": {
                "found": False,
                "reason": "No profile found",
                "profile_image": None
            },
            "TikTok": {
                "found": True,
                "username": "@cyber_user",
                "followers": 4200,
                "profile_image": "https://i.pravatar.cc/150?u=tiktok_cyber_user"
            },
            "YouTube": {
                "found": False,
                "reason": "No channel found",
                "profile_image": None
            },
            "Snapchat": {
                "found": True,
                "username": "cyber_user",
                "score": 9999,
                "profile_image": "https://i.pravatar.cc/150?u=snapchat_cyber_user"
            },
            "Reddit": {
                "found": True,
                "username": "u/cyber_user",
                "karma": 42000,
                "profile_image": "https://i.pravatar.cc/150?u=reddit_cyber_user"
            },
            "Discord": {
                "found": True,
                "tag": "cyber_user#0001",
                "profile_image": "https://i.pravatar.cc/150?u=discord_cyber_user"
            },
            "Telegram": {
                "found": True,
                "username": "@cyber_user",
                "profile_image": "https://i.pravatar.cc/150?u=telegram_cyber_user"
            },
            "WhatsApp": {
                "found": True,
                "status": "Living in the net 🌐",
                "profile_image": "https://i.pravatar.cc/150?u=whatsapp_cyber_user"
            }
        }
        
        if platform in mock_data:
            data = mock_data[platform]
            return SearchResult(
                platform=platform,
                found=data["found"],
                details=data
            )
        return SearchResult(
            platform=platform,
            found=False,
            details={"status": "Platform not supported"}
        )
    except Exception as e:
        logger.error(f"Error checking {platform}: {str(e)}")
        return SearchResult(platform=platform, found=False)

async def check_financial_platform(phone: str, platform: str) -> SearchResult:
    """Check if phone number is associated with a financial platform"""
    try:
        # Mock data for demonstration
        mock_data = {
            "Cash App": {"found": True, "username": "$cyber_user", "verified": True},
            "Venmo": {"found": True, "username": "@cyber_user", "transactions": 420},
            "PayPal": {"found": True, "email": "cyber_user@neo.city"},
            "Zelle": {"found": True, "linked_bank": "Neo City Bank"},
            "Apple Pay": {"found": True, "devices": 3},
            "Google Pay": {"found": True, "last_used": "2077-06-21"},
            "Amazon Pay": {"found": False, "reason": "No account found"},
            "Coinbase": {"found": True, "verified_level": "Advanced"},
            "Crypto.com": {"found": True, "status": "Active"},
            "Kraken": {"found": True, "account_tier": "Pro"},
            "Charles Schwab": {"found": False, "reason": "No account found"},
            "E*TRADE": {"found": True, "account_type": "Premium"},
            "TD Ameritrade": {"found": True, "status": "Active"},
            "Webull": {"found": True, "account_level": "Level 2"},
            "Robinhood": {"found": True, "status": "Active Trader"}
        }
        
        if platform in mock_data:
            data = mock_data[platform]
            return SearchResult(
                platform=platform,
                found=data["found"],
                details=data
            )
        return SearchResult(
            platform=platform,
            found=False,
            details={"status": "Platform not supported"}
        )
    except Exception as e:
        logger.error(f"Error checking {platform}: {str(e)}")
        return SearchResult(platform=platform, found=False)

async def get_additional_info(phone: str) -> Dict[str, Any]:
    """Get additional OSINT information about the phone number"""
    try:
        headers = {
            "X-RapidAPI-Key": API_CONFIG["rapidapi"]["key"],
            "X-RapidAPI-Host": API_CONFIG["rapidapi"]["osint"]["host"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_CONFIG['rapidapi']['osint']['url']}?phone={phone}",
                headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": "Failed to get additional info"}
    except Exception as e:
        logger.error(f"Error getting additional info: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

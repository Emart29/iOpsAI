# backend/middleware/rate_limit.py
"""Rate limiting middleware to prevent API abuse"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio


class RateLimitMiddleware(BaseHTT):
    """
    Rater.
    Uses in-memory storage (for production, consider Redis).
    """
    
    def 
        self, 
        app
        requests_per_minute: int = 60, 
        reque= 1000
    ):
        super().__init__(app)
        self.requests_penute
        sehour
        # Store: {ip: [(timestamp, minute_count, , ...]}
        self.requst)
       minutes
        self.last_cleanup = datetime.utcnow
    
    def _get_cli
        """Extract client IP from request"""
        # Check for forwarded header)
        forwarded = request.headers.get("X-Forwarded-Fo
        if forwarded:
     )
        return request.clientn"
    
    def _cleanup_old_entries(self):
        """Remove entries""
     
        if (now - self.last_cleanup).seconds < self.cleanup_interval:
            return
        
        cutoff = now - timedelta(hours=1)
        for ip in list(sel
 = [
                entry for entry in self.request_counts[ip]
                if entry[0] > cutoff
            ]
        ts[ip]:
                del self.request_counts[ip]
        
   w
    
    def _check_rate_limit(self, ip: str) -> Tup]:
        """Check if request should be r""
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        hour
        
    ts
        recent_requests = self.request_counts[ip]
        
        # Count requests 
        minute_count = sum(1 finute_ago)
        hour_count = sum(1 for ts, _, _ in recent_requ
        
        # Check limits
        if minute_count >= self.requests_per_
      "
        if hou
            return False, f"Rate limit exceeded: {self.requests_per_hour} req"
        
        # Add current request
        self.request_counts[ip].append
  ""
    
    async def dispatch(self, reque:
        # Skip rate limiting fchecks
        if request.url.path == "/health":
            return await call_next(request)
        
        # C
        self._cleanup_old_entries()
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        allowed, message = s_ip)
        if not allowed:       raise HTTPException(status_code=esponse
turn r
        re
        r)s_per_houestlf.requ = str(seimit-Hour"]mit-LeLiers["X-Ratnse.head    responute)
    r_miequests_pe.rstr(selfMinute"] = -Limit-RateLimitX-["headerse.onsresps
        aderimit heate l r      # Add        
  t)
esqul_next(re= await cal  response      
    
     sage) detail=mes429,
     
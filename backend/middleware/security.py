# backend/middleware/security.py
"""Security middleware for input validation, sanitization, and XSS/SQL injection protection"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Resp
from typing import Any, Dict, Optional
import re
in


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middlewars.
    """
    
    # SQL 
    SQL_PATTERNS = [
        re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
        re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IG
        re.compile(r"(\bINSERT\b.*\bINTO\b.*\bVALUES\b)", re.IGNORECASE),
        re.compile(r
        re.compile(r"(\bUPDATE\b.*\bSET\b)", rE),
    s
        re.compile(r"(\bOR\b\s+\d+\s*=\s*\d+)", re.IGNORECASE),  # OR 1=1
        re.compile(r"(\bAND\b\s+\dND 1=1
OR '
    ]
    
    erns
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</scrLL),
        re.compile(r'javar)e, ststance(valusin       if int"""
 ntes cocioufor malies k valu checvelycursi""Re   "tr]:
     [sonalti "") -> Op path: str =: Any,lf, valueue(seck_valf _chede    )
    
      7;")
  x2"'", "&#.replace(    
        uot;")e('"', "&q .replac       ")
    , "&gt;e(">"lacrep .       t;")
     "&le("<",lac       .rep
      "&amp;")"&",e(   .replac       ue
         valrn (
        retu""
     r output"coding foy en HTML entit"""Basic     > str:
    -str)lue: f, varing(selanitize_stef _s   de
    
  Fals   return  rn True
           retu
        ch(value):n.sear   if patter      :
   ERNSS_PATTXSin self.ttern for pa   
     s"""SS pattern X contains if valueheck"C     ""bool:
   ) -> : str valueself,eck_xss( _ch  def   
   False
 return        n True
retur             value):
   arch(pattern.se  if          TERNS:
 f.SQL_PATrn in selpatteor       fs"""
  rnection patte SQL injntains if value co"Check    ""ool:
    e: str) -> bvalulf, tion(sejec_sql_in_check   def ]
    
 ts/upload"datase"/api/upload", "/api/_PATHS = [)
    SKIPratelydled sepaoads han file uple.g.,ation (p validths to ski  # Pa   
]
   n
    pressioSS ex),  # C.IGNORECASE*\(', repression\smpile(r'exco   re.SE),
     IGNORECAoad', re.[^>]*onl'<svgmpile(r       re.coCASE),
  re.IGNOREembed',ompile(r'<      re.cASE),
  , re.IGNORECobject'r'<le(mpi      re.coRECASE),
  me', re.IGNO(r'<ifra.compile
        rer, etc.ick, onerroSE),  # onclECAe.IGNOR\w+\s*=', r(r'on.compile     re),
   CASE re.IGNOREscript:',
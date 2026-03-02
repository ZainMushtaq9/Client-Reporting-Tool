import random
from datetime import date

def generate_metrics(client_id: int, period_start: date, period_end: date) -> dict:
    """
    Returns all report metrics for a client and period.
    Deterministic: same client_id + period always returns identical values.
    """
    seed = client_id * 1000 + period_start.year * 12 + period_start.month
    r = random.Random(seed)
    
    metrics = {}
    
    # ── Website Traffic ──────────────────────────────
    metrics["sessions"]          = r.randint(1200, 8000)
    metrics["users"]             = r.randint(900, 6000)
    metrics["pageviews"]         = r.randint(3000, 20000)
    metrics["bounce_rate"]       = round(r.uniform(35.0, 70.0), 1)    # %
    metrics["avg_session_dur"]   = r.randint(60, 240)                 # seconds
    metrics["sessions_change"]   = round(r.uniform(-15.0, 35.0), 1)   # % change vs prev period
    metrics["users_change"]      = round(r.uniform(-15.0, 35.0), 1)
    
    # ── Traffic Sources (values sum to 100) ─────────
    metrics["source_organic"]    = r.randint(28, 45)    # %
    metrics["source_direct"]     = r.randint(15, 28)
    metrics["source_social"]     = r.randint(10, 22)
    metrics["source_referral"]   = r.randint(5, 14)
    metrics["source_paid"]       = 100 - sum([metrics["source_organic"], metrics["source_direct"], metrics["source_social"], metrics["source_referral"]])
    
    # ── Top Pages (list of 5 dicts) ──────────────────
    metrics["top_pages"] = [
        {"page": "/",         "views": r.randint(800,2000), "bounce": round(r.uniform(30,60),1)},
        {"page": "/services", "views": r.randint(300,900),  "bounce": round(r.uniform(30,60),1)},
        {"page": "/about",    "views": r.randint(200,700),  "bounce": round(r.uniform(40,70),1)},
        {"page": "/blog",     "views": r.randint(150,600),  "bounce": round(r.uniform(40,70),1)},
        {"page": "/contact",  "views": r.randint(100,400),  "bounce": round(r.uniform(20,50),1)},
    ]
    
    # ── SEO / Search Console ─────────────────────────
    metrics["impressions"]       = r.randint(5000, 40000)
    metrics["clicks"]            = r.randint(300, 3000)
    metrics["ctr"]               = round(r.uniform(1.5, 8.0), 2)      # %
    metrics["avg_position"]      = round(r.uniform(3.0, 25.0), 1)     # avg SERP rank
    metrics["top_keywords"] = [
        {"keyword": "brand name",    "clicks": r.randint(100,500), "position": round(r.uniform(1.0,5.0),1)},
        {"keyword": "main service",  "clicks": r.randint(50,200),  "position": round(r.uniform(3.0,10.0),1)},
        {"keyword": "local keyword", "clicks": r.randint(30,150),  "position": round(r.uniform(5.0,15.0),1)},
    ]
    
    # ── Paid Ads ──────────────────────────────────────
    metrics["ad_spend"]          = round(r.uniform(500, 5000), 2)      # USD
    metrics["ad_impressions"]    = r.randint(10000, 80000)
    metrics["ad_clicks"]         = r.randint(200, 3000)
    metrics["ad_ctr"]            = round(r.uniform(1.0, 5.0), 2)
    metrics["ad_cpc"]            = round(r.uniform(0.50, 4.00), 2)     # cost per click
    metrics["ad_conversions"]    = r.randint(5, 100)
    metrics["ad_cost_per_conv"]  = round(r.uniform(10, 150), 2)
    metrics["ad_roas"]           = round(r.uniform(1.5, 6.0), 2)       # return on ad spend
    
    # ── Email Marketing ──────────────────────────────
    metrics["emails_sent"]       = r.randint(500, 5000)
    metrics["email_open_rate"]   = round(r.uniform(18.0, 42.0), 1)     # %
    metrics["email_ctr"]         = round(r.uniform(1.5, 8.0), 1)
    metrics["email_unsub_rate"]  = round(r.uniform(0.1, 0.8), 2)
    
    # ── Conversions ───────────────────────────────────
    metrics["goal_completions"]  = r.randint(10, 200)
    metrics["conversion_rate"]   = round(r.uniform(1.0, 6.0), 2)       # %
    metrics["revenue"]           = round(r.uniform(1000, 20000), 2)     # USD
    
    return metrics

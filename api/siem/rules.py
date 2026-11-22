SEVERITY = {
    0: "INFO",
    1: "LOW",
    2: "MEDIUM",
    3: "HIGH",
    4: "CRITICAL",
}

RULES = (
    {
        "id": "BRUTE_FORCE",
        "name": "Failed login burst",
        "event_type": "auth_failure",
        "group_by": ("src_ip", "user"),
        "distinct": None,
        "threshold": 5,
        "window_seconds": 300,
        "severity": 4,
        "mitre": "T1110",
    },
    {
        "id": "PORT_SCAN",
        "name": "Horizontal port scan",
        "event_type": "connection",
        "group_by": ("src_ip",),
        "distinct": "target",
        "threshold": 8,
        "window_seconds": 300,
        "severity": 2,
        "mitre": "T1046",
    },
    {
        "id": "WEB_SCAN",
        "name": "Web path enumeration",
        "event_type": "http_404",
        "group_by": ("src_ip",),
        "distinct": "target",
        "threshold": 10,
        "window_seconds": 600,
        "severity": 2,
        "mitre": "T1595",
    },
)

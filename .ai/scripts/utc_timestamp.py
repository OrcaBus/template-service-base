#!/usr/bin/env python3
"""Print the current UTC time as YYYY-MM-DDTHHMMSSZ (no colons, safe in file names).

Used by the update-dependencies skill to name its run logs. Standard library only.
"""

from datetime import datetime, timezone

print(datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ'))

from datetime import datetime
from typing import Any, Optional

from deta import Base


def log(data: dict[str, Any], expire_in: Optional[int] = 60 * 60 * 2) -> None:
    time = datetime.now()
    data.update({'time': time.isoformat()})

    logging_base = Base('logs')
    logging_base.put(
        key=str(2 * 10**9 - time.timestamp()),
        data=data,
        expire_in=expire_in
    )

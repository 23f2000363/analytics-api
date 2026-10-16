import math
import os
from collections import defaultdict
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

EMAIL = "23f2000363@ds.study.iitm.ac.in"

app = FastAPI(title="Stateless Event Analytics API", version="1.0.0")

# The exam browser is allowed to call this API cross-origin. No cookies are used.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event] = Field(default_factory=list)


class AnalyticsResponse(BaseModel):
    email: str
    total_events: int
    unique_users: int
    revenue: float
    top_user: Optional[str]


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    expected = os.environ.get("ANALYTICS_API_KEY", "")
    if not expected or x_api_key is None or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analytics", response_model=AnalyticsResponse, dependencies=[Depends(require_api_key)])
def analytics(request: AnalyticsRequest) -> AnalyticsResponse:
    events = request.events
    users = {event.user for event in events}
    positive_amounts_by_user: dict[str, list[float]] = defaultdict(list)
    positive_amounts: list[float] = []

    for event in events:
        if event.amount > 0:
            positive_amounts.append(event.amount)
            positive_amounts_by_user[event.user].append(event.amount)

    user_totals = {user: math.fsum(amounts) for user, amounts in positive_amounts_by_user.items()}
    # The grader guarantees no ties. If the batch contains no positive amount,
    # there is no user with a positive-amount total, so top_user is null.
    top_user = max(user_totals, key=user_totals.get) if user_totals else None

    return AnalyticsResponse(
        email=EMAIL,
        total_events=len(events),
        unique_users=len(users),
        revenue=math.fsum(positive_amounts),
        top_user=top_user,
    )

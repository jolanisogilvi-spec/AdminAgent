from fastapi import APIRouter
from app.api.v1 import ai_agent, approvals, assets, auth, configs, knowledge, tasks, tickets, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(configs.router, prefix="/configs", tags=["System Config"])
api_router.include_router(ai_agent.router, prefix="/ai", tags=["AI Agent"])

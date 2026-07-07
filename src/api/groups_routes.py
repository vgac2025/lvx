"""Group REST routes — GROUPES_RESEAUX_ARTCB v1.1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from artcb.groups.manager import (
    ForbiddenGroupAction,
    FounderImmutableError,
    GroupError,
    GroupManager,
)

logger = logging.getLogger("artcb.api.groups")
router = APIRouter(prefix="/api/v1/groups", tags=["groups"])


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    founder_address: str = Field(min_length=8)


class ActorRequest(BaseModel):
    actor_address: str = Field(min_length=8)


class InviteMemberRequest(ActorRequest):
    address: str = Field(min_length=8)
    role: str = "contributor"


class SetRoleRequest(ActorRequest):
    role: str


class DissolveGroupRequest(ActorRequest):
    confirm: str


def _groups(request: Request) -> GroupManager:
    return request.app.state.artcb.groups


def _group_http_error(exc: GroupError) -> HTTPException:
    if isinstance(exc, FounderImmutableError):
        logger.debug("FOUNDER_IMMUTABLE blocked: %s", exc)
        return HTTPException(status_code=403, detail={"code": exc.code, "message": str(exc)})
    if isinstance(exc, ForbiddenGroupAction):
        return HTTPException(status_code=403, detail={"code": exc.code, "message": str(exc)})
    return HTTPException(status_code=400, detail={"code": exc.code, "message": str(exc)})


@router.post("")
def create_group(body: CreateGroupRequest, request: Request) -> dict:
    mgr = _groups(request)
    group = mgr.create_group(body.name, body.founder_address)
    logger.debug("Group created id=%s founder=%s", group.group_id, group.founder_address)
    return group.to_dict()


@router.get("")
def list_groups(
    request: Request,
    address: str = Query(..., min_length=8, description="Wallet address du membre"),
) -> dict:
    mgr = _groups(request)
    groups = mgr.list_groups_for_address(address)
    return {"groups": [g.to_dict() for g in groups], "count": len(groups)}


@router.get("/{group_id}")
def get_group(group_id: str, request: Request) -> dict:
    mgr = _groups(request)
    group = mgr.get_group(group_id)
    if not group or group.dissolved:
        raise HTTPException(status_code=404, detail="group not found")
    return group.to_dict()


@router.post("/{group_id}/members")
def invite_member(group_id: str, body: InviteMemberRequest, request: Request) -> dict:
    mgr = _groups(request)
    try:
        group = mgr.add_member(group_id, body.actor_address, body.address, body.role)  # type: ignore[arg-type]
    except GroupError as exc:
        raise _group_http_error(exc) from exc
    return group.to_dict()


@router.post("/{group_id}/members/{target_address}/role")
def set_member_role(
    group_id: str,
    target_address: str,
    body: SetRoleRequest,
    request: Request,
) -> dict:
    mgr = _groups(request)
    try:
        group = mgr.set_member_role(
            group_id,
            body.actor_address,
            target_address,
            body.role,  # type: ignore[arg-type]
        )
    except GroupError as exc:
        raise _group_http_error(exc) from exc
    return group.to_dict()


@router.delete("/{group_id}/members/{target_address}")
def remove_member(
    group_id: str,
    target_address: str,
    request: Request,
    actor_address: str = Query(..., min_length=8),
) -> dict:
    mgr = _groups(request)
    try:
        group = mgr.remove_member(group_id, actor_address, target_address)
    except GroupError as exc:
        raise _group_http_error(exc) from exc
    return group.to_dict()


@router.post("/{group_id}/dissolve")
def dissolve_group(group_id: str, body: DissolveGroupRequest, request: Request) -> dict:
    mgr = _groups(request)
    try:
        group = mgr.dissolve_group(group_id, body.actor_address, body.confirm)
    except GroupError as exc:
        raise _group_http_error(exc) from exc
    return group.to_dict()

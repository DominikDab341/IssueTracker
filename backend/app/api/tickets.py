from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, Depends, Query

from app.api.dependencies import get_processing_runtime, get_ticket_service
from app.api.schemas import (
    TaskStatusResponse, TicketCloseResponse, TicketCreate, TicketCreateResponse,
    TicketEdit, TicketEditResponse, TicketResponse, TicketStatusUpdate,
    AssignmentUpdate, AssignmentResponse, CategoryUpdate, PriorityUpdate,
    SuggestedDuplicate,
)
from app.domain import Priority
from app.services.processing import ProcessingRuntime
from app.services.tickets import TicketService
from app.ticket_status import TicketStatus


router = APIRouter(prefix="/tickets")


@router.patch("/{ticket_id}/category", response_model=TicketResponse)
async def correct_category(ticket_id: int, body: CategoryUpdate, service: TicketService = Depends(get_ticket_service)):
    return await service.correct_category(ticket_id, body.category, expected_content_version=body.expected_content_version)


@router.patch("/{ticket_id}/assignee", response_model=TicketResponse)
async def assign_ticket(ticket_id: int, body: AssignmentUpdate, service: TicketService = Depends(get_ticket_service)):
    return await service.assign(ticket_id, body.assignee_id)


@router.get("/{ticket_id}/assignments", response_model=list[AssignmentResponse])
async def assignment_history(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    return await service.assignment_history(ticket_id)


@router.patch("/{ticket_id}/priority", response_model=TicketResponse)
async def manual_priority(ticket_id: int, body: PriorityUpdate, service: TicketService = Depends(get_ticket_service)):
    return await service.set_priority(ticket_id, body.priority)


@router.get("/", response_model=list[TicketResponse])
async def get_tickets(
    status: TicketStatus | None = None,
    category: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    priority: Priority | Literal["unknown"] | None = None,
    needs_review: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    service: TicketService = Depends(get_ticket_service),
):
    return await service.list_tickets(status=status, category=category, priority=priority,
                                      needs_review=needs_review, limit=limit, offset=offset)


@router.get("/{ticket_id}/duplicates", response_model=list[SuggestedDuplicate])
async def suggested_duplicates(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    return await service.duplicates(ticket_id)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: int, service: TicketService = Depends(get_ticket_service)):
    return await service.get(ticket_id)


@router.post("/", response_model=TicketCreateResponse, status_code=201)
async def create_ticket(body: TicketCreate, background_tasks: BackgroundTasks,
                        service: TicketService = Depends(get_ticket_service),
                        runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket, task = await service.create(text=body.text, work_blocked=body.work_blocked, run_id=runtime.run_id)
    background_tasks.add_task(runtime.process, task.id)
    return TicketCreateResponse(ticket=ticket, task_id=task.id)


@router.get("/{ticket_id}/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(ticket_id: int, task_id: str, service: TicketService = Depends(get_ticket_service)):
    task, current = await service.get_task(ticket_id, task_id)
    return TaskStatusResponse(
        task_id=task.id, state=task.state, content_version=task.content_version, current=current,
        created_at=task.created_at, started_at=task.started_at, finished_at=task.finished_at,
        result=task.result, error=task.error, error_code=task.error_code,
    )


@router.post("/{ticket_id}/classification/retry", response_model=TicketCreateResponse, status_code=202)
async def retry_classification(ticket_id: int, background_tasks: BackgroundTasks,
                                service: TicketService = Depends(get_ticket_service),
                                runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket, task = await service.retry_classification(ticket_id, run_id=runtime.run_id)
    background_tasks.add_task(runtime.process, task.id)
    return TicketCreateResponse(ticket=ticket, task_id=task.id)


@router.patch("/{ticket_id}", response_model=TicketEditResponse)
async def edit_ticket(ticket_id: int, body: TicketEdit, background_tasks: BackgroundTasks,
                      service: TicketService = Depends(get_ticket_service),
                      runtime: ProcessingRuntime = Depends(get_processing_runtime)):
    ticket, task = await service.edit(ticket_id, text=body.text, work_blocked=body.work_blocked, run_id=runtime.run_id)
    if task is not None:
        background_tasks.add_task(runtime.process, task.id)
    return TicketEditResponse(ticket=ticket, task_id=ticket.current_task_id)


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(ticket_id: int, body: TicketStatusUpdate,
                               service: TicketService = Depends(get_ticket_service)):
    return await service.change_status(ticket_id, status=body.status,
                                        resolution_note=body.resolution_note, rejection_reason=body.rejection_reason)


@router.delete("/{ticket_id}", response_model=TicketCloseResponse, deprecated=True)
async def delete_ticket(ticket_id: int, body: TicketStatusUpdate,
                        service: TicketService = Depends(get_ticket_service)):
    """Zgodność ze starym adresem: jawny status końcowy, bez usuwania rekordu."""
    ticket, duplicates = await service.close(ticket_id, status=body.status,
                                             resolution_note=body.resolution_note, rejection_reason=body.rejection_reason)
    return TicketCloseResponse(ticket=ticket, status=ticket.status, suggested_duplicates=duplicates)

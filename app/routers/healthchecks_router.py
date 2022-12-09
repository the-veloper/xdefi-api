from fastapi import APIRouter, status, Request, Response

from app.schemas.responses_schema import Healthcheck, Degraded


router = APIRouter()


@router.get(
    "/liveness",
    response_model=Healthcheck,
    status_code=status.HTTP_200_OK,
)
async def liveness_healthcheck():
    return Healthcheck(status=True)


@router.get(
    "/readiness",
    response_model=Healthcheck,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: dict(model=Degraded)}
)
async def readiness_healthcheck(
    request: Request,
    response: Response,
):
    healthcheck_status = False
    if len(request.app.state.uniswap_pairs):
        healthcheck_status = True
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return Healthcheck(status=healthcheck_status)

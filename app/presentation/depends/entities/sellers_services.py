from typing import Annotated

from fastapi import Depends

from app.application.services.sellers_services import SellerServices
from app.infrastructure.depends.entities.sellers_services import (
    get_sellers_services_infr,
)


def get_sellers_services(
    services: Annotated[SellerServices, Depends(get_sellers_services_infr)],
) -> SellerServices:
    return services

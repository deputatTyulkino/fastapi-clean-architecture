from typing import Annotated

from fastapi import Depends

from app.application.services.categories_services import CategoryServices
from app.infrastructure.depends.categories_services import get_categories_services_infr


def get_categories_services(
    services: Annotated[CategoryServices, Depends(get_categories_services_infr)],
) -> CategoryServices:
    return services

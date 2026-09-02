from typing import Annotated

from fastapi import Depends

from app.application.services.products_services import ProductServices
from app.infrastructure.depends.entities.products_services import (
    get_products_services_infr,
)


def get_product_services(
    services: Annotated[ProductServices, Depends(get_products_services_infr)],
) -> ProductServices:
    return services

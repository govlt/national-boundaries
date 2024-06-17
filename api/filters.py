from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

import models


class MunicipalityFilter(Filter):
    code__in: Optional[list[str]] = None
    name__ilike: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = models.Municipalities

        # search_model_fields = ["id", "name", "code", "area_ha"]


class CountiesFilter(Filter):
    code__in: Optional[list[str]] = None
    name__ilike: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = models.Municipalities

        # search_model_fields = ["id", "name", "code", "area_ha"]


class EldershipsFilter(Filter):
    code__in: Optional[list[str]] = None
    name__ilike: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = models.Elderships

        # search_model_fields = ["id", "name", "code", "area_ha"]


class ResidentialAreasFilter(Filter):
    code__in: Optional[list[str]] = None
    name__ilike: Optional[str] = None
    order_by: Optional[list[str]] = None

    class Constants(Filter.Constants):
        model = models.ResidentialAreas

        # search_model_fields = ["id", "name", "code", "area_ha"]

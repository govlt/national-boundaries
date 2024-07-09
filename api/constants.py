from typing import Dict

from fastapi import Query
from fastapi.openapi.models import Example

query_srid: Query = Query(
    3346,
    openapi_examples={
        "example_wgs": {
            "summary": "WGS 84 (EPSG:4326)",
            "description": "The World Geodetic System (WGS 84) coordinate reference system.",
            "value": 4326
        },
        "example_lks": {
            "summary": "LKS 94 (EPSG:3346)",
            "description": "The Lithuanian Coordinate System (LKS 94) reference system.",
            "value": 3346
        },
    },
    description="A spatial reference identifier (SRID) for geometry output."
)

openapi_examples_geometry_filtering: Dict[str, Example] = {
    "example_ewkb": {
        "summary": "Filter using EWKB and 'intersects'",
        "description": "Filter geometries using hexed EWKB (Extended Well-Known Binary) format and the 'intersects' method. SRID is mandatory.",
        "value": {
            "geometry": {
                "method": "intersects",
                "ewkb": "0103000020E6100000010000000500000045F6419605473940B1DD3D40F7574B4045F641960547394061E124CD1F574B40719010E50B4A394061E124CD1F574B40719010E50B4A3940B1DD3D40F7574B4045F6419605473940B1DD3D40F7574B40"
            }
        }
    },
    "example_ewkt": {
        "summary": "Filter using EWKT and 'intersects'",
        "description": "Filter geometries using EWKT (Extended Well-Known Text) format with the default 'intersects' method. SRID is mandatory.",
        "value": {
            "geometry": {
                "ewkt": "SRID=4326;POLYGON((25.277429 54.687233, 25.277429 54.680658, 25.289244 54.680658, 25.289244 54.687233, 25.277429 54.687233))"
            }
        }
    },
    "example_geojson": {
        "summary": "Filter using GeoJSON and 'contains'",
        "description": "Filter geometries using GeoJSON format and the 'contains' method. CRS is mandatory.",
        "value": {
            "geometry": {
                "method": "contains",
                "geojson": "{\"crs\":{\"type\":\"name\",\"properties\":{\"name\":\"EPSG:4326\"}},"
                           "\"type\":\"Polygon\",\"coordinates\":[[[25.277429,54.687233],"
                           "[25.277429,54.680658],[25.289244,54.680658],[25.289244,54.687233],"
                           "[25.277429,54.687233]]]}"
            }
        }
    }
}

openapi_examples_counties_filtering: Dict[str, Example] = {
    "example_counties_codes": {
        "summary": "Filter by county codes",
        "description": "Retrieve data for counties by specifying county codes.",
        "value": {
            "counties": {
                "codes": [5, 10]
            }
        }
    },
    "example_counties_feature_ids": {
        "summary": "Filter by county feature IDs",
        "description": "Retrieve data for counties by specifying feature IDs.",
        "value": {
            "counties": {
                "feature_ids": [3, 9]
            }
        }
    },
    "example_counties_name_starts": {
        "summary": "Filter by county name prefix",
        "description": "Retrieve data for counties where names start with the specified prefix.",
        "value": {
            "counties": {
                "name": {
                    "starts": "alyt"
                }
            }
        }
    },
    "example_counties_name_exact": {
        "summary": "Filter by county exact name",
        "description": "Retrieve data for counties matching the exact specified name.",
        "value": {
            "counties": {
                "name": {
                    "exact": "Panevėžio apskr."
                }
            }
        }
    },
    "example_counties_name_contains": {
        "summary": "Filter by county name substring",
        "description": "Retrieve data for counties where names contain the specified substring.",
        "value": {
            "counties": {
                "name": {
                    "contains": "no"
                }
            }
        }
    }
}

openapi_examples_municipalities_filtering: Dict[str, Example] = {
    "example_municipalities_codes": {
        "summary": "Filter by municipality codes",
        "description": "Retrieve data for municipalities by specifying municipality codes.",
        "value": {
            "municipalities": {
                "codes": [21, 23]
            }
        }
    },
    "example_municipalities_feature_ids": {
        "summary": "Filter by municipality feature IDs",
        "description": "Retrieve data for municipalities by specifying feature IDs.",
        "value": {
            "municipalities": {
                "feature_ids": [6, 37]
            }
        }
    },
    "example_municipalities_name_starts": {
        "summary": "Filter by municipality name prefix",
        "description": "Retrieve data for municipalities where names start with the specified prefix.",
        "value": {
            "municipalities": {
                "name": {
                    "starts": "nerin"
                }
            }
        }
    },
    "example_municipalities_name_exact": {
        "summary": "Filter by municipality exact name",
        "description": "Retrieve data for municipalities matching the exact specified name.",
        "value": {
            "municipalities": {
                "name": {
                    "exact": "Klaipėdos m. sav."
                }
            }
        }
    },
    "example_municipalities_name_contains": {
        "summary": "Filter by municipality name substring",
        "description": "Retrieve data for municipalities where names contain the specified substring.",
        "value": {
            "municipalities": {
                "name": {
                    "contains": "r."
                }
            }
        }
    }
}

openapi_examples_elderships_filtering: Dict[str, Example] = {
    "example_elderships_codes": {
        "summary": "Filter by eldership codes",
        "description": "Retrieve data for elderships by specifying eldership codes.",
        "value": {
            "elderships": {
                "codes": [1302, 1303]
            }
        }
    },
    "example_elderships_feature_ids": {
        "summary": "Filter by eldership feature IDs",
        "description": "Retrieve data for elderships by specifying feature IDs.",
        "value": {
            "elderships": {
                "feature_ids": [37, 282]
            }
        }
    },
    "example_elderships_name_starts": {
        "summary": "Filter by eldership name prefix",
        "description": "Retrieve data for elderships where names start with the specified prefix.",
        "value": {
            "elderships": {
                "name": {
                    "starts": "Lazdynų"
                }
            }
        }
    },
    "example_elderships_name_exact": {
        "summary": "Filter by eldership exact name",
        "description": "Retrieve data for elderships matching the exact specified name.",
        "value": {
            "elderships": {
                "name": {
                    "exact": "Naujamiesčio sen."
                }
            }
        }
    },
    "example_elderships_name_contains": {
        "summary": "Filter by eldership name substring",
        "description": "Retrieve data for elderships where names contain the specified substring.",
        "value": {
            "elderships": {
                "name": {
                    "contains": "miesčio"
                }
            }
        }
    }
}

openapi_examples_residential_areas_filtering: Dict[str, Example] = {
    "example_residential_areas_codes": {
        "summary": "Filter by residential area codes",
        "description": "Retrieve data for residential areas by specifying residential area codes.",
        "value": {
            "residential_areas": {
                "codes": [10184, 10264]
            }
        }
    },
    "example_residential_areas_feature_ids": {
        "summary": "Filter by residential area feature IDs",
        "description": "Retrieve data for residential areas by specifying feature IDs.",
        "value": {
            "residential_areas": {
                "feature_ids": [279, 15942]
            }
        }
    },
    "example_residential_areas_name_starts": {
        "summary": "Filter by residential area name prefix",
        "description": "Retrieve data for residential areas where names start with the specified prefix.",
        "value": {
            "residential_areas": {
                "name": {
                    "starts": "adomavos"
                }
            }
        }
    },
    "example_residential_areas_name_exact": {
        "summary": "Filter by residential area exact name",
        "description": "Retrieve data for residential areas matching the exact specified name.",
        "value": {
            "residential_areas": {
                "name": {
                    "exact": "Aščiagalių k."
                }
            }
        }
    },
    "example_residential_areas_name_contains": {
        "summary": "Filter by residential area name substring",
        "description": "Retrieve data for residential areas where names contain the specified substring.",
        "value": {
            "residential_areas": {
                "name": {
                    "contains": "vs."
                }
            }
        }
    }
}

openapi_examples_streets_filtering: Dict[str, Example] = {
    "example_streets_codes": {
        "summary": "Filter by street codes",
        "description": "Retrieve data for streets by specifying street codes.",
        "value": {
            "streets": {
                "codes": [1207622, 1611772]
            }
        }
    },
    "example_streets_feature_ids": {
        "summary": "Filter by street feature IDs",
        "description": "Retrieve data for streets by specifying feature IDs.",
        "value": {
            "streets": {
                "feature_ids": [19910, 21783]
            }
        }
    },
    "example_streets_name_starts": {
        "summary": "Filter by street name prefix",
        "description": "Retrieve data for streets where names start with the specified prefix.",
        "value": {
            "streets": {
                "name": {
                    "starts": "žemaičių"
                }
            }
        }
    },
    "example_streets_name_exact": {
        "summary": "Filter by street exact name",
        "description": "Retrieve data for streets matching the exact specified name.",
        "value": {
            "streets": {
                "name": {
                    "exact": "Žemaičių g."
                }
            }
        }
    },
    "example_streets_name_contains": {
        "summary": "Filter by street name substring",
        "description": "Retrieve data for streets where names contain the specified substring.",
        "value": {
            "streets": {
                "name": {
                    "contains": "al."
                }
            }
        }
    }
}

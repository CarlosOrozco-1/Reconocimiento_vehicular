from __future__ import annotations


def mock_routes_geojson() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": 1, "route_code": "CA-1", "name": "CA-1 Occidente"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-90.733, 14.62], [-91.48, 14.78]],
                },
            },
            {
                "type": "Feature",
                "properties": {"id": 2, "route_code": "CA-9", "name": "CA-9 Sur"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[-90.506, 14.634], [-90.33, 14.28]],
                },
            },
        ],
    }


def mock_peak_hours() -> list[dict]:
    return [
        {
            "route_code": "CA-1",
            "route_name": "CA-1 Occidente",
            "peak_hour": 7,
            "avg_flow": 980,
        },
        {
            "route_code": "CA-9",
            "route_name": "CA-9 Sur",
            "peak_hour": 17,
            "avg_flow": 1220,
        },
    ]


def mock_departments_geojson() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": 1, "code": "GT-01", "name": "Guatemala"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-90.75, 14.45],
                            [-90.30, 14.45],
                            [-90.30, 14.85],
                            [-90.75, 14.85],
                            [-90.75, 14.45],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"id": 2, "code": "GT-03", "name": "Sacatepequez"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-90.88, 14.40],
                            [-90.58, 14.40],
                            [-90.58, 14.67],
                            [-90.88, 14.67],
                            [-90.88, 14.40],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"id": 3, "code": "GT-05", "name": "Escuintla"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-90.65, 13.90],
                            [-90.15, 13.90],
                            [-90.15, 14.45],
                            [-90.65, 14.45],
                            [-90.65, 13.90],
                        ]
                    ],
                },
            },
        ],
    }


def mock_route_departments(route_code: str) -> list[dict]:
    base = {
        "CA-1": ["Guatemala", "Sacatepequez"],
        "CA-9": ["Guatemala", "Escuintla"],
    }
    names = base.get(route_code, [])
    return [
        {
            "route_code": route_code,
            "route_name": f"{route_code} Route",
            "department_code": f"MOCK-{index}",
            "department_name": name,
        }
        for index, name in enumerate(names, start=1)
    ]


def mock_route_summary(route_code: str) -> dict:
    defaults = {
        "CA-1": {"route_name": "CA-1 Occidente", "normal_flow": 760, "peak_flow": 980, "peak_hour": 7},
        "CA-9": {"route_name": "CA-9 Sur", "normal_flow": 910, "peak_flow": 1220, "peak_hour": 17},
    }
    selected = defaults.get(
        route_code,
        {"route_name": route_code, "normal_flow": 0, "peak_flow": 0, "peak_hour": None},
    )
    return {
        "route_code": route_code,
        "route_name": selected["route_name"],
        "normal_flow": selected["normal_flow"],
        "peak_flow": selected["peak_flow"],
        "peak_hour": selected["peak_hour"],
    }

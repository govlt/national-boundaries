from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_counties_by_code():
    response = client.post(
        "/v1/counties/search",
        json={"counties": {"codes": [5, 10]}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for county in data["items"]:
        assert "code" in county


def test_search_counties_by_name_starts():
    response = client.post(
        "/v1/counties/search",
        json={"counties": {"name": {"starts": "alyt"}}}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    for county in data["items"]:
        assert "name" in county
        assert county["name"].lower().startswith("alyt")


def test_get_county_by_code():
    response = client.get("/v1/counties/10")
    if response.status_code == 200:
        county = response.json()
        assert county["code"] == 10
    elif response.status_code == 404:
        error = response.json()
        assert error["detail"] == "County not found"


def test_get_county_with_geometry_by_code():
    response = client.get("/v1/counties/10/geometry?srid=4326")
    if response.status_code == 200:
        county = response.json()
        assert county["code"] == 10
        assert "geometry" in county
    elif response.status_code == 404:
        error = response.json()
        assert error["detail"] == "County not found"


def test_validation_error_search():
    response = client.post(
        "/v1/counties/search",
        json={"counties": "invalid_value"}
    )
    assert response.status_code == 422
    error = response.json()
    assert "detail" in error

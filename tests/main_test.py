from uuid import uuid4

from fastapi.testclient import TestClient
from fastapi import status

from math import cos, sin, radians

from polycut.models import CutInfo
from polycut.main import app
# from debug2D import plot_cut # disable for pytest

client = TestClient(app)


def test_fetch_cuts():
    response = client.get("/api/poly-cut")
    assert response.status_code == status.HTTP_200_OK


def test_update_cut():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 1, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 0.5, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_200_OK
    id = response.json()
    assert id is not None

    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 10, "y": 10, "z": 0},
            {"x": 10, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 0.5, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.put(f"/api/poly-cut/{id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    result = client.get(f"/api/poly-cut/{id}")
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()["result"]["result_polygons"]) == 2


def test_update_non_existing():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 1, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 0, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    random_id = uuid4()
    response = client.put(f"/api/poly-cut/{random_id}", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_post_simple_cut():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 1, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 0.5, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_200_OK
    id = response.json()
    assert id is not None
    result = client.get(f"/api/poly-cut/{id}")
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()["result"]["result_polygons"]) == 2
    # cut = Cut(**result.json())
    # plot_cut(cut)


def test_dense_circle():
    # generate circle polygon
    polygon = []
    for i in range(0, 3600, 1):
        angle = radians(i / 10)
        polygon.append(
            {
                "x": cos(angle),
                "y": sin(angle),
                "z": 0,
            }
        )
    data = {
        "polygon": polygon,
        "plane_origin": {"x": 0, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }
    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_200_OK
    id = response.json()
    assert id is not None
    result = client.get(f"/api/poly-cut/{id}")
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()["result"]["result_polygons"]) == 2
    # cut = Cut(**result.json())
    # plot_cut(cut)


def test_polygon_invalid():
    data = {
        "polygon": [
            {"x": 0},
            {"x": 1},
            {"x": 1},
        ],
        "plane_origin": {"x": 0, "y": 0, "z": 0},
        "plane_normal": {"x": 0, "y": 0, "z": 1},
    }
    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_post_non_planar():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 1, "y": 0, "z": 0},
            {"x": 1, "y": 0, "z": 1},
        ],
        "plane_origin": {"x": 0, "y": 0, "z": 0},
        "plane_normal": {"x": 0, "y": 0, "z": 1},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_polygon_not_on_xy_plane


def test_post_non_orthogonal_plane():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 1, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 0, "y": 0, "z": 0},
        "plane_normal": {"x": 0, "y": 0, "z": 1},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_cut_plane_not_orthogonal


def test_self_intersecting_polygon():
    self_intersecting_polygon = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 2, "y": 0, "z": 0},
            {"x": 3, "y": 1, "z": 0},
            {"x": 4, "y": 0, "z": 0},
            {"x": 5, "y": 1, "z": 0},
        ],
        "plane_origin": {"x": 0, "y": 0.5, "z": 0},
        "plane_normal": {"x": 0, "y": 1, "z": 0},
    }

    response = client.post("/api/poly-cut", json=self_intersecting_polygon)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_polygon_not_convex


def test_edge_tangent():
    edge_tangent = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 2, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 1, "y": 0, "z": 0},
        "plane_normal": {"x": 0, "y": 1, "z": 0},
    }

    response = client.post("/api/poly-cut", json=edge_tangent)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_line_tangent_to_segment


def test_cut_through_vertex():
    cut_through_vertex = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
            {"x": 2, "y": 0, "z": 0},
        ],
        "plane_origin": {"x": 1, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.post("/api/poly-cut", json=cut_through_vertex)
    assert response.status_code == status.HTTP_200_OK


def test_empty_polygon():
    data = {
        "polygon": [],
        "plane_origin": {"x": 1, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_polygon_less_than_three_vertices


def test_two_vertices_polygon():
    data = {
        "polygon": [
            {"x": 0, "y": 0, "z": 0},
            {"x": 1, "y": 1, "z": 0},
        ],
        "plane_origin": {"x": 1, "y": 0, "z": 0},
        "plane_normal": {"x": 1, "y": 0, "z": 0},
    }

    response = client.post("/api/poly-cut", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == CutInfo.failed_polygon_less_than_three_vertices

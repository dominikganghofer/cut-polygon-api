from typing import List
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class Vector2D(BaseModel):
    x: float
    y: float


class Vector3D(BaseModel):
    x: float
    y: float
    z: float


class CutRequest(BaseModel):
    polygon: List[Vector3D]
    plane_origin: Vector3D
    plane_normal: Vector3D


class CutInfo(str, Enum):
    failed_no_intersection = "failed_no_intersection"
    failed_line_vertex_tangent = "failed_line_vertex_tangent"
    failed_line_tangent_to_segment = "failed_line_on_polygon"
    failed_cut_plane_not_orthogonal = "failed_cut_plane_not_orthogonal"
    failed_polygon_not_on_xy_plane = "failed_polygon_not_on_xy_plane"
    failed_polygon_not_convex = "failed_polygon_not_convex"
    failed_polygon_less_than_three_vertices = "failed_polygon_less_than_three_vertices"
    successful = "successful"


class CutResult(BaseModel):
    info: CutInfo
    result_polygons: List[List[Vector3D]]


class Cut(BaseModel):
    id: UUID
    request: CutRequest
    result: CutResult


class Intersection(BaseModel):
    index: int
    position: Vector2D

from typing import List
import numpy as np

from polycut.models import Vector2D, Vector3D, CutInfo, CutRequest, CutResult, Intersection

epsilon = 1e-6


def try_cut_polygon(request: CutRequest) -> CutResult:
    """ Try to cut a polygon with a plane """
    # check if polygon is on XY plane
    if not all(v.z == 0 for v in request.polygon):
        return CutResult(info=CutInfo.failed_polygon_not_on_xy_plane, result_polygons=[])

    # check if plane is orthogonal to XY plane
    if not (request.plane_normal.z == 0):
        return CutResult(info=CutInfo.failed_cut_plane_not_orthogonal, result_polygons=[])

    # convert to 2D
    polygon2d = [Vector2D(x=v.x, y=v.y) for v in request.polygon]
    line_origin2d = Vector2D(x=request.plane_origin.x, y=request.plane_origin.y)
    line_normal2d = Vector2D(x=request.plane_normal.x, y=request.plane_normal.y)

    # remove duplicate points from polygon
    polygon2d = [x for i, x in enumerate(polygon2d) if not are_equal(x, polygon2d[(i + 1) % len(polygon2d)])]

    # check if polygon is valid
    if len(polygon2d) < 3:
        return CutResult(info=CutInfo.failed_polygon_less_than_three_vertices, result_polygons=[])

    # check if line lies on polygon
    if is_line_tangent_to_poly_segment(polygon2d, line_origin2d, line_normal2d):
        return CutResult(info=CutInfo.failed_line_tangent_to_segment, result_polygons=[])

    # find intersections
    intersections = []
    for i, v1 in enumerate(polygon2d):
        v2 = polygon2d[(i + 1) % len(polygon2d)]
        intersection = intersect_curve_with_line(v1, v2, line_origin2d, line_normal2d)
        if intersection is not None:
            intersections.append(Intersection(index=i, position=intersection))

    # remove intersections that are too close to each other
    intersections = [x for i, x in enumerate(intersections) if
                     not are_equal(x.position, intersections[(i + 1) % len(intersections)].position)]

    if len(intersections) == 0:
        # no intersections, polygon is not cut
        return CutResult(info=CutInfo.success_no_cut, result_polygons=[])

    if len(intersections) == 1:
        # one intersection, polygon touched at vertex
        return CutResult(info=CutInfo.failed_line_vertex_tangent, result_polygons=[])

    # accepts non-convex polygons if they are cut in two
    # todo: discuss if non-convex input should be caught earlier; might be too expensive for large polygons
    if len(intersections) > 2:
        return CutResult(info=CutInfo.failed_polygon_not_convex, result_polygons=[])

    result_polygons = cut_polygon(polygon2d, intersections[0], intersections[1])

    # convert back to 3D
    result_polygons = [[Vector3D(x=v.x, y=v.y, z=0) for v in polygon] for polygon in result_polygons]

    return CutResult(info=CutInfo.successful, result_polygons=result_polygons)


def cut_polygon(polygon: List[Vector2D], first: Intersection, second: Intersection) -> List[List[Vector2D]]:
    """ Cut a polygon in two """
    left_polygon = []
    right_polygon = []
    for i, v in enumerate(polygon):
        if i < first.index or i > second.index:
            left_polygon.append(v)
        if i == first.index:
            left_polygon.append(v)
            left_polygon.append(first.position)
            right_polygon.append(first.position)
        if first.index < i < second.index:
            right_polygon.append(v)
        if i == second.index:
            right_polygon.append(v)
            right_polygon.append(second.position)
            left_polygon.append(second.position)
    return [left_polygon, right_polygon]


def intersect_curve_with_line(curve_start: Vector2D, curve_end: Vector2D, line_origin: Vector2D,
                              line_normal: Vector2D) -> Vector2D:
    """ Find intersection between a line and a curve segment """

    def to_np(v):
        return np.array([v.x, v.y])

    c_start = to_np(curve_start)
    c_end = to_np(curve_end)
    l_origin = to_np(line_origin)
    l_normal = to_np(line_normal)

    c_direction = c_end - c_start
    denominator = np.dot(l_normal, c_direction)
    if abs(denominator) < epsilon:
        # line is parallel to plane
        return None
    t = np.dot(l_origin - c_start, l_normal) / denominator
    if t < 0 or t > 1:
        # intersection is outside the line segment
        return None
    intersection = c_start + t * c_direction
    return Vector2D(x=intersection[0], y=intersection[1])


def is_line_tangent_to_poly_segment(polygon: List[Vector2D], line_origin: Vector2D, line_normal: Vector2D) -> bool:
    """ Check if a line is tangent to a polygon segment """
    for i, v1 in enumerate(polygon):
        v2 = polygon[(i + 1) % len(polygon)]
        if is_point_on_line(v1, line_origin, line_normal) and is_point_on_line(v2, line_origin, line_normal):
            return True
    return False


def is_point_on_line(point: Vector2D, line_origin: Vector2D, line_normal: Vector2D) -> bool:
    """ Check if a point is on a line """
    distance = distance_to_line(point, line_origin, line_normal)
    return abs(distance) < epsilon


def distance_to_line(point: Vector2D, line_origin: Vector2D, line_normal: Vector2D) -> float:
    """ Calculate distance between a point and a line """
    p = np.array([point.x, point.y])
    o = np.array([line_origin.x, line_origin.y])
    n = np.array([line_normal.x, line_normal.y])
    c = np.dot(p - o, n)
    norm = np.linalg.norm(n)
    return c / norm


def are_equal(v1: Vector2D, v2: Vector2D) -> bool:
    """ Check if two vectors are equal """
    return abs(v1.x - v2.x) < epsilon and abs(v1.y - v2.y) < epsilon

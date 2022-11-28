from polycut.models import Cut, CutInfo, CutRequest, CutResult, Vector2D
import polycut.calculations as calc


def test_are_equal_true():
    assert calc.are_equal(Vector2D(x=1, y=1), Vector2D(x=1, y=1))


def test_are_equal_false():
    assert not calc.are_equal(Vector2D(x=1, y=1), Vector2D(x=1, y=2))


def test_are_equal_tolerance():
    assert calc.are_equal(Vector2D(x=1, y=1), Vector2D(x=1.0000000000000001, y=1))


def test_distance_to_line():
    assert calc.distance_to_line(Vector2D(x=1, y=1), Vector2D(x=0, y=0), Vector2D(x=-2, y=2)) == 0


def test_is_point_on_line():
    assert calc.is_point_on_line(Vector2D(x=0, y=1), Vector2D(x=1, y=0), Vector2D(x=2, y=2))


def test_is_line_tangent_to_polygon_segment():
    assert calc.is_line_tangent_to_poly_segment([Vector2D(x=0, y=0), Vector2D(x=1, y=0), Vector2D(x=1, y=1)],
                                                Vector2D(x=0, y=0), Vector2D(x=-1, y=1))


def test_intersect_curve_with_line():
    assert calc.intersect_curve_with_line(Vector2D(x=0, y=0), Vector2D(x=1, y=1), Vector2D(x=0, y=1),
                                          Vector2D(x=1, y=1)) == Vector2D(x=0.5, y=0.5)


def test_cut_polygon():
    polygon = [Vector2D(x=0, y=0), Vector2D(x=1, y=0), Vector2D(x=1, y=1), Vector2D(x=0, y=1)]
    first = calc.Intersection(index=0, position=Vector2D(x=0.5, y=0))
    second = calc.Intersection(index=2, position=Vector2D(x=.5, y=1))
    result = calc.cut_polygon(polygon, first, second)
    assert len(result) == 2
    # TODO: check the result

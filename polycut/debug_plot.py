import matplotlib.pyplot as plt
from polycut.models import Cut, Vector2D


def plot_cut(cut: Cut):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # plot polygon
    xs = [v.x for v in cut.request.polygon]
    ys = [v.y for v in cut.request.polygon]
    xs.append(xs[0])
    ys.append(ys[0])
    ax.scatter(xs, ys)
    ax.plot(xs, ys)

    # plot line
    start = cut.request.plane_origin
    direction = Vector2D(x=-cut.request.plane_normal.y, y=cut.request.plane_normal.x)
    end = Vector2D(x=start.x + direction.x, y=start.y + direction.y)
    xs = [start.x,  end.x]
    ys = [start.y,  end.y]
    ax.scatter(xs, ys)
    ax.plot(xs, ys)

    # plot result
    offset = 0.1
    result = cut.result.result_polygons
    for polygon in result:
        xs = [v.x + offset for v in polygon]
        ys = [v.y + offset for v in polygon]
        xs.append(xs[0])
        ys.append(ys[0])
        ax.scatter(xs, ys)
        ax.plot(xs, ys)

    plt.show()

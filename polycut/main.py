from uuid import uuid4

from typing import List
from fastapi import FastAPI, HTTPException

from polycut.calculations import try_cut_polygon
from polycut.models import CutResult, CutRequest, Cut, CutInfo, CutRequestUpdate

app = FastAPI()
db: dict[str, Cut] = {}


@app.get("/")
def index():
    return {
        "polycut_api": "/api/poly-cut",
        "documentation": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/poly-cut", response_model=List[Cut])
def fetch_cuts():
    """ Fetch all cuts """
    # return db as list
    return [cut for cut in db.values()]


@app.post("/api/poly-cut", response_model=str)
def post_cut_request(request: CutRequest):
    """Post a cut request and return the id of the cut"""
    result = try_cut_polygon(request)
    match result.info:
        case CutInfo.failed_no_intersection:
            raise HTTPException(status_code=400, detail=str(CutInfo.failed_no_intersection))
        case CutInfo.failed_line_vertex_tangent:
            raise HTTPException(status_code=400, detail=CutInfo.failed_line_vertex_tangent)
        case CutInfo.failed_line_tangent_to_segment:
            raise HTTPException(status_code=400, detail=CutInfo.failed_line_tangent_to_segment)
        case CutInfo.failed_cut_plane_not_orthogonal:
            raise HTTPException(status_code=400, detail=CutInfo.failed_cut_plane_not_orthogonal)
        case CutInfo.failed_polygon_not_on_xy_plane:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_not_on_xy_plane)
        case CutInfo.failed_polygon_not_convex:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_not_convex)
        case CutInfo.failed_polygon_less_than_three_vertices:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_less_than_three_vertices)
        case CutInfo.successful:
            cut_id = str(uuid4())
            cut = Cut(id=cut_id, request=request, result=result)
            db[cut_id] = cut
            return cut_id


@app.put("/api/poly-cut/{id}")
def put_cut_request(update: CutRequestUpdate):
    """Update a cut request"""
    if update.id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")

    result = try_cut_polygon(update.request)
    match result.info:
        case CutInfo.failed_no_intersection:
            raise HTTPException(status_code=400, detail=str(CutInfo.failed_no_intersection))
        case CutInfo.failed_line_vertex_tangent:
            raise HTTPException(status_code=400, detail=CutInfo.failed_line_vertex_tangent)
        case CutInfo.failed_line_tangent_to_segment:
            raise HTTPException(status_code=400, detail=CutInfo.failed_line_tangent_to_segment)
        case CutInfo.failed_cut_plane_not_orthogonal:
            raise HTTPException(status_code=400, detail=CutInfo.failed_cut_plane_not_orthogonal)
        case CutInfo.failed_polygon_not_on_xy_plane:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_not_on_xy_plane)
        case CutInfo.failed_polygon_not_convex:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_not_convex)
        case CutInfo.failed_polygon_less_than_three_vertices:
            raise HTTPException(status_code=400, detail=CutInfo.failed_polygon_less_than_three_vertices)
        case CutInfo.successful:
            cut = Cut(id=update.id, request=update.request, result=result)
            db[update.id] = cut
            return update.id


@app.get("/api/poly-cut/{id}", response_model=Cut)
def fetch_cut(id: str):
    """Fetch a cut by its id"""
    if id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")
    return db[id]


@app.delete("/api/poly-cut/{id}")
def delete_cut(id: str):
    """Delete a cut by its id"""
    if id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")
    del db[id]
    return None

from typing import List
from uuid import uuid4, UUID
from fastapi import FastAPI, HTTPException

from polycut.calculations import try_cut_polygon
from polycut.models import CutResult, CutRequest, Cut, CutInfo

app = FastAPI()
db: dict[UUID, Cut] = {}


@app.get("/api/poly-cut", response_model=List[CutResult])
def fetch_cuts():
    """ Fetch all cuts """
    # return db as list
    return [cut for cut in db.values()]


@app.post("/api/poly-cut")
def post_cut_request(request: CutRequest, response_model=UUID):
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
            cut_id = uuid4()
            cut = Cut(id=cut_id, request=request, result=result)
            db[cut_id] = cut
            return cut_id


@app.put("/api/poly-cut/{cut_id}")
def put_cut_request(cut_id: UUID, request: CutRequest):
    """Update a cut request"""
    if cut_id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")

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
            cut = Cut(id=cut_id, request=request, result=result)
            db[cut_id] = cut
            return cut_id


@app.get("/api/poly-cut/{cut_id}", response_model=Cut)
def fetch_cut(cut_id: UUID):
    """Fetch a cut by its id"""
    if cut_id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")
    return db[cut_id]


@app.delete("/api/poly-cut/{id}")
def delete_cut(cut_id: UUID):
    """Delete a cut by its id"""
    if cut_id not in db.keys():
        raise HTTPException(status_code=404, detail="Cut not found")
    del db[cut_id]
    return

from typing import Union
from typing import List
from fastapi import FastAPI
from fastapi import FastAPI, Header
from pydantic import BaseModel
app = FastAPI()

class ManageEC2(BaseModel):
    ec2ids: List[str]
    ec2regions: List[str]
    

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


@app.post("https://astjo9g2mb.execute-api.us-east-1.amazonaws.com/prod/v1/user/{userid}/action/{actionid}")
def manageEC2( userid:str, actionid:str,item:ManageEC2,Authorization: Union[str, None] = Header()):

    return {"userid": userid, "actionid": actionid,"body":item,"Authorization":Authorization}
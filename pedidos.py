import os 
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse 
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr 
from bson import ObjectId  
from typing import Optional, List 
import motor.motor_asyncio 

app = FastAPI()


MONGODB_URL = 'mongodb+srv://danieldonado:Daniel.300@cluster0.utkzs04.mongodb.net/test'
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.misiontic


class PyObjectId(ObjectId):
    @classmethod 
    def __get_validators__(cls):
        yield cls.validate 
          
    @classmethod 
    def validate(cls, v): 
        if not ObjectId.is_valid(v): 
            raise ValueError("Invalid objectid") 
        return ObjectId(v)

    @classmethod 
    def __modify_schema__(cls, field_schema): 
        field_schema.update(type="string")

class PedidosModel(BaseModel):
   id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") 
   cantidad: int = Field(..., le=1000) 
   descripcion: str = Field(...)
   metodo_pago: str = Field(...)  
   

   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "cantidad": "1",
                "descripcion": "Pedido 10",
                "metodo_pago": "tarjeta de Credito o PSE"
                
           } 
        } 

class UpdatePedidosModel(BaseModel): 
   cantidad: Optional[int]
   descripcion: Optional[str] 
   metodo_pago: Optional[str] 

   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "cantidad": "1",
                "descripcion": "Pedido 10",
                "metodo_pago": "tarjeta de Credito o PSE"
           }  
        }       

@app.post("/", response_description="Add new pedido",response_model=PedidosModel) 
async def create_pedidos(pedido: PedidosModel = Body(...)): 
   pedido = jsonable_encoder(pedido) 
   new_pedido = await db["pedidos"].insert_one(pedido) 
   created_pedido = await db["pedido"].find_one({"_id": new_pedido.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_pedido)

@app.get("/", response_description="List all pedidos",response_model=List[PedidosModel] )
async def list_pedidos(): 
   pedidos = await db["pedidos"].find().to_list(1000) 
   return pedidos

@app.get("/{id}", response_description="Get a single pedidos",response_model=PedidosModel ) 
async def show_pedidos(id: str): 
    if (pedido := await db["pedidos"].find_one({"_id": id})) is not None: 
        return pedido

    raise HTTPException(status_code=404, detail=f"Pedido {id} not found")

    
@app.put("/", response_description="Update a pedido", response_model=PedidosModel) 
async def update_pedidos(id: str, pedido: UpdatePedidosModel = Body(...)): 
    pedido = {k: v for k, v in pedido.dict().items() if v is not None}  
    
    if len(pedido) >= 1: 
     update_result = await db["pedidos"].update_one({"_id": id}, {"$set": pedido})
   
     if update_result.modified_count == 1: 
          if (
               updated_pedido := await db["pedidos"].find_one({"_id":id}) 
             )is not None:
             return updated_pedido
   
    if (existing_pedido := await db["pedidos"].find_one({"_id":id})) is not None:
        return existing_pedido

    raise HTTPException(status_code=404, detail=f"Pedido {id} not found")


@app.delete("/{id}", response_description="Delete a pedido") 
async def delete_pedidos(id: str): 
    delete_result = await db["pedidos"].delete_one({"_id": id}) 

    if delete_result.deleted_count == 1: 
       return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"Pedido {id} not found")
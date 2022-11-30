import os 
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse 
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr 
from bson import ObjectId  
from typing import Optional, List 
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio 

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)


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

class VehiculosModel(BaseModel):
   id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") 
   marca: str = Field(...)
   modelo: str = Field(...) 
   año: int = Field(..., le=10000)
   tipo: str = Field(...)  
   precio: int = Field(..., le=10000000000)

   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "marca": "Chevrolet",
                "modelo": "NLR",
                "año": "2018",
                "tipo": "Carga",
                "precio": "30.000.000"
           } 
        } 

class UpdateVehiculosModel(BaseModel): 
   marca: Optional[str] 
   modelo: Optional[str] 
   año: Optional[int] 
   tipo: Optional[str]
   precio: Optional[int]

   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "marca": "Chevrolet",
                "modelo": "NLR",
                "año": "2018",
                "tipo": "Carga",
                "precio": "30.000.000"
           }  
        }       

@app.post("/", response_description="Add new vehiculo",response_model=VehiculosModel) 
async def create_vehiculo(vehiculo: VehiculosModel = Body(...)): 
   vehiculo = jsonable_encoder(vehiculo) 
   new_vehiculo = await db["vehiculos"].insert_one(vehiculo) 
   created_vehiculo = await db["vehiculo"].find_one({"_id": new_vehiculo.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_vehiculo)

@app.get("/", response_description="List all vehiculos",response_model=List[VehiculosModel] )
async def list_vehiculos(): 
   vehiculos = await db["vehiculos"].find().to_list(1000) 
   return vehiculos

@app.get("/{id}", response_description="Get a single vehiculo",response_model=VehiculosModel ) 
async def show_vehiculos(id: str): 
    if (vehiculo := await db["vehiculos"].find_one({"_id": id})) is not None: 
        return vehiculo

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")

    
@app.put("/", response_description="Update a vehiculo", response_model=VehiculosModel) 
async def update_vehiculo(id: str, vehiculo: UpdateVehiculosModel = Body(...)): 
    vehiculo = {k: v for k, v in vehiculo.dict().items() if v is not None}  
    
    if len(vehiculo) >= 1: 
     update_result = await db["vehiculos"].update_one({"_id": id}, {"$set": vehiculo})
   
     if update_result.modified_count == 1: 
          if (
               updated_vehiculo := await db["vehiculos"].find_one({"_id":id}) 
             )is not None:
             return updated_vehiculo
   
    if (existing_vehiculo := await db["vehiculos"].find_one({"_id":id})) is not None:
        return existing_vehiculo

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")


@app.delete("/{id}", response_description="Delete a Vehiculo") 
async def delete_vehiculo(id: str): 
    delete_result = await db["vehiculos"].delete_one({"_id": id}) 

    if delete_result.deleted_count == 1: 
       return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"vehiculo {id} not found")


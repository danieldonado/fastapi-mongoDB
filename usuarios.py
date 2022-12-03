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

class UsuariosModel(BaseModel):
   id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") 
   Nombre: str = Field(...)
   email: EmailStr = Field(...) 
   direccion: str = Field(...)
   pais: str = Field(...)  
   tel: int = Field(..., le=10000000000)

   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "nombre": "Jane Doe",
                "email": "jdoe@example.com",
                "direccion": "Cl 15 # 15 - 00",
                "pais": "Colombia",
                "tel": "300 000 0000"
           } 
        } 

class UpdateUsuariosModel(BaseModel): 
   nombre: Optional[str]
   email: Optional[EmailStr] 
   direccion: Optional[str] 
   pais: Optional[str] 
   tel: Optional[int]

   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "nombre": "Jane Doe",
                "email": "jdoe@example.com",
                "direccion": "Cl 15 # 15 - 00",
                "pais": "Colombia",
                "tel": "300 451 2444"
           }  
        }       

@app.post("/", response_description="Add new usuario",response_model=UsuariosModel) 
async def create_usuario(usuario: UsuariosModel = Body(...)): 
   usuario = jsonable_encoder(usuario) 
   new_usuario = await db["usuarios"].insert_one(usuario) 
   created_usuario = await db["usuario"].find_one({"_id": new_usuario.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_usuario)

@app.get("/", response_description="List all usuarios",response_model=List[UsuariosModel] )
async def list_usuarios(): 
   usuarios = await db["usuarios"].find().to_list(1000) 
   return usuarios

@app.get("/{id}", response_description="Get a single usuario",response_model=UsuariosModel ) 
async def show_usuario(id: str): 
    if (usuario := await db["usuarios"].find_one({"_id": id})) is not None: 
        return usuario

    raise HTTPException(status_code=404, detail=f"Usuario {id} not found")

    
@app.put("/", response_description="Update a usuario", response_model=UsuariosModel) 
async def update_usuario(id: str, usuario: UpdateUsuariosModel = Body(...)): 
    usuario = {k: v for k, v in usuario.dict().items() if v is not None}  
    
    if len(usuario) >= 1: 
     update_result = await db["usuarios"].update_one({"_id": id}, {"$set": usuario})
   
     if update_result.modified_count == 1: 
          if (
               updated_usuario := await db["usuarios"].find_one({"_id":id}) 
             )is not None:
             return updated_usuario
   
    if (existing_usuario := await db["usuarios"].find_one({"_id":id})) is not None:
        return existing_usuario

    raise HTTPException(status_code=404, detail=f"Usuario {id} not found")


@app.delete("/{id}", response_description="Delete a usuario") 
async def delete_usuario(id: str): 
    delete_result = await db["usuarios"].delete_one({"_id": id}) 

    if delete_result.deleted_count == 1: 
       return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"Usuario {id} not found")


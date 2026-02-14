#pydantic is used for validation of errors and data types in fastapi
from pydantic import BaseModel

#class uses the BaseModel from pydantic to create a model for products with the following fields: id, name, quantity, quality and decs. The id field is optional and can be None, while the other fields are required. The class also has an __init__ method that initializes the fields with the given values. also by using the baseModel we can able to add the required fields init!
class products(BaseModel):
    id: int | None = None
    name: str
    quantity: int
    quality: str
    decs: str

    
    ##this is for the normal class without using the baseModel from pydantic(without using the model class)
    # def __init__(self, id: int, name: str, quantity: int, quality: str, decs: str) -> None:
    #     self.id = id
    #     self.name = name
    #     self.quantity = quantity
    #     self.quality = quality
    #     self.decs = decs
    
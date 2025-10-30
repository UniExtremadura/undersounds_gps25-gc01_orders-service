from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator
from model.order_model_ import OrderStatus
from datetime import datetime

class BuyerDTO(BaseModel):
     name: str
     username: str


class SellerDTO(BaseModel):
     name: str
     username: str
     pfp: str

     model_config = ConfigDict(from_attributes=True)

class OrderItemDTO(BaseModel):
     publicId: str
     name: str
     imageSrc: str
     description: str
     seller: SellerDTO # Diccionario con sus datos, proporcionado por Pydantic
     quantity: int
     price: float
     total: float   

     @classmethod
     def from_orm(cls, item):
          return cls(
               publicId=item.product_public_id,
               name=item.product_name,
               imageSrc=item.product_image_src or "",
               description=item.product_description or "",
               seller=SellerDTO(
                    name=item.seller_name,
                    username=item.seller_username,
                    pfp=item.seller_pfp or ""
               ),
               quantity=item.quantity,
               price=float(item.price),
               total=float(item.total)
          )

class OrderResponseDTO(BaseModel):
     publicId: str
     madeBy: BuyerDTO
     items: list[OrderItemDTO]
     createdAt: str
     status: OrderStatus
     total: float

     @classmethod
     def from_orm(cls, order):
          try:
               # String conversion of OrderStatus
               status_str = order.status.value if hasattr(order.status, 'value') else str(order.status)

               # Management of created_at
               if order.created_at is None:
                    created_at_str = datetime.utcnow().isoformat() + 'Z'
               elif hasattr(order.created_at, 'isoformat'):
                    created_at_str = order.created_at.isoformat() + 'Z'
               else:
                    created_at_str = str(order.created_at)

               return cls(
                    publicId=order.public_id,
                    madeBy=BuyerDTO(
                         name=order.made_by_username,  # Temporal - después obtendrás el nombre real
                         username=order.made_by_username
                    ),
                    items=[OrderItemDTO.from_orm(item) for item in order.items],
                    createdAt=created_at_str,
                    status=status_str,
                    total=float(order.total)
               )
          except Exception as e:
               print(f"❌ Error en OrderResponseDTO.from_orm: {e}")
               raise e

class CreateOrderItemRequestDTO(BaseModel):
     productId: str
     quantity: int

     @field_validator('quantity')
     def quantity_must_be_positive(cls, v):
          if v <= 0:
               raise ValueError('La cantidad debe ser mayor a 0')
          return v

class CreateOrderRequestDTO(BaseModel):
     items: list[CreateOrderItemRequestDTO]

class OrderPageDTO(BaseModel):
     content: list[OrderResponseDTO]
     totalElements: int
     totalPages: int

     model_config = ConfigDict(from_attributes=True)
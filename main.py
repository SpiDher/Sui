from fastapi import FastAPI,HTTPException,status,Depends
from pydantic import BaseModel,BeforeValidator 
from typing import Annotated,Any
from pysui.abstracts.client_keypair import SignatureScheme
from pysui.sui.sui_config import SuiConfig
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db,Base,engine
from models import BaseUser
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError
from pysui.sui.sui_crypto import SuiKeyPair,create_new_address
import requests
from sqlalchemy.future import select
from sqlalchemy.engine import Result



@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
app = FastAPI(lifespan=lifespan,title='Sheda Solutions Backend',version='0.1.0',docs_url='/',description='Backend for SUI Hack')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = SuiConfig.user_config(rpc_url='https://sui-testnet-endpoint.blockvision.org')

BILL_URL = 'https://www.nellobytesystems.com/APICancelV1.asp'
        
def hash_pin(pwd:Any):
    return pwd_context.hash(pwd)

class WalletCreate(BaseModel):
    username: str
    pin:Annotated[str,BeforeValidator(hash_pin)]
    
    class Config:
        from_attributes = True


DBSession = Annotated[AsyncSession,Depends(get_db)]


@app.post('/create-wallet',status_code=status.HTTP_201_CREATED,response_model=dict)
async def create_wallet(payload:WalletCreate,db:DBSession):
    #keypair = gen_mnemonic_phrase(12)
    wallet = create_new_address(word_counts=12,keytype=SignatureScheme.ED25519)
    mnemonics,keypair,address = wallet
    new_user = BaseUser(**payload.model_dump())
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT,detail='user exists')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detial=str(e))
        
    return {'wallet':address.address,'mnemonics':mnemonics,'keypair':keypair}

#NOTE -  Working
@app.post('/get-balance/{address}',status_code=status.HTTP_200_OK,response_model=dict)
async def get_balance(address:str):
    ...
    
@app.get('/check-username/{username}',status_code=status.HTTP_200_OK,response_model=dict)
async  def check_username(username:str,db:DBSession):
    query = select(BaseUser).where(BaseUser.username == username)
    result:Result = db.execute(query)
    username = result.scalars().first()
    if username:
        return {'exists':True}
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail='Not found')

@app.post('/buy-airtime',status_code=status.HTTP_200_OK,response_model=dict)
async def buy_airtime(phone_no:str):
    params = {
    "UserID": "your_userid",
    "APIKey": "your_apikey",
    "OrderID": "order_id"
}
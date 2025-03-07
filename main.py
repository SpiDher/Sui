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
from sui_sdk import Wallet,Client


@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        conn.run_sync(Base.metadata.create_all)
app = FastAPI(lifespan=lifespan,title='Sheda Solutions Backend',version='0.1.0',docs_url='/',description='Backend for SUI Hack')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = SuiConfig.default_config()


        
def hash_pin(pwd:Any):
    return pwd_context.hash(pwd)

class WalletCreate(BaseModel):
    username: str
    pin:Annotated[str,BeforeValidator(hash_pin)]
    
    class Config:
        from_attributes = True


DBSession = Annotated[AsyncSession,Depends(get_db)]


app.post('/create-wallet',status_code=status.HTTP_201_CREATED,response_model=dict)
async def create_wallet(payload:WalletCreate,db:DBSession):
    try:
        mnemonics, ddress = config.create_new_keypair_and_address(SignatureScheme.ED25519)
    except Exception:
        wallet = Wallet.generate()
        address = wallet.get_address()
        mnemonics = wallet.mnemonic
    new_user = BaseUser(**payload.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {'wallet':address.address,'mnemonics':mnemonics}

app.post('/get-balance/{address}',status_code=status.HTTP_200_OK,response_model=dict)
async def get_balance(address:str):
    client = Client("https://fullnode.testnet.sui.io")
    balance = client.get_balance(address)
    return {'balance':balance}


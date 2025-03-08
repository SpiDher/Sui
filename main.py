from fastapi import FastAPI,HTTPException,status,Depends
from pydantic import BaseModel,BeforeValidator,Field
from typing import Annotated,Any,Optional
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
from dotenv import load_dotenv
import os
import aiofiles
import json
from pysui.sui.sui_clients.sync_client import SuiClient
from pysui.sui.sui_builders.get_builders import GetCoins
#from pysui.sui.sui_types.scalars import SuiAddress
load_dotenv()

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
app = FastAPI(lifespan=lifespan,title='Sheda Solutions Backend',version='0.1.0',docs_url='/',description='Backend for SUI Hack')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = SuiConfig.user_config(rpc_url='https://fullnode.mainnet.sui.io:443')
client = SuiClient(config=config)
BILL_URL = 'https://www.nellobytesystems.com/APICancelV1.asp'

API_KEY = os.getenv('API_KEY')
BASE_DIR = os.path.join(os.getcwd())
        
def hash_pin(pwd:Any):
    return pwd_context.hash(pwd)

class WalletCreate(BaseModel):
    username: str
    pin:Annotated[str,BeforeValidator(hash_pin)]
    address:Optional[str] = None
    
    class Config:
        from_attributes = True


DBSession = Annotated[AsyncSession,Depends(get_db)]


@app.post('/create-wallet',status_code=status.HTTP_201_CREATED,response_model=dict)
async def create_wallet(payload:WalletCreate,db:DBSession):
    #keypair = gen_mnemonic_phrase(12)
    wallet = create_new_address(word_counts=12,keytype=SignatureScheme.ED25519)
    mnemonics,keypair,address = wallet
    new_user = BaseUser(**payload.model_dump(exclude=['address']),address= address.address)
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT,detail='user exists')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detail=str(e))
        
    return {'wallet':address.address,'mnemonics':mnemonics,'private_key':keypair.private_key.to_b64()}

#NOTE -  Working
@app.get('/get-balance/{address}',status_code=status.HTTP_200_OK,response_model=dict)
async def get_balance(address:str):
    coins_response = client.execute(GetCoins(owner=address))
    if coins_response.is_ok():
        coins = coins_response.result_data.data
        total_balance = sum(int(coin.balance) for coin in coins)
        print(f"Total balance: {total_balance} SUI")
        return {'balance':str(total_balance)}
    else:
        print(f"Error fetching balance: {coins_response.result_string}")
    
@app.post('/check-username/{username}',status_code=status.HTTP_200_OK,response_model=WalletCreate)
async  def check_username(username:str,db:DBSession):
    query = select(BaseUser).where(BaseUser.username == username)
    result:Result = await db.execute(query)
    user = result.scalars().first()
    if user:
        return user
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail='Not found')

@app.post('/buy-airtime',status_code=status.HTTP_200_OK,response_model=dict)
async def buy_airtime(phone_no:str,amount:str,network:str):
    params = {
    "UserID": "Penivera",
    "APIKey": API_KEY,
    "MobileNetwork": network,
    "Amount": amount,
    "MobileNumber": phone_no,
    "CallBackURL": "https://cypher-85fk.onrender.com/callback"
    }
    response = requests.get(BILL_URL,params=params)
    return response.json()

@app.get('/payment-result',status_code=status.HTTP_200_OK,response_model=dict)
async def  payment_result():
    async with aiofiles.open(os.path.join(BASE_DIR,'data.json'),'r') as file:
        data = json.loads(await file.read())    
    return data

@app.post('/callback', status_code=status.HTTP_200_OK)
async def save_data(data: dict):
    if data:
        file_path = os.path.join(BASE_DIR, 'data.json')
        async with aiofiles.open(file_path, 'w') as file:
            await file.write(json.dumps(data, indent=4))  # Properly serialize data
    return {"message": "Data saved successfully"}


data = {
    "MOBILE_NETWORK": {
        "MTN": [
            {
                "ID": "01",
                "PRODUCT": [
                    {"PRODUCT_CODE": "2", "PRODUCT_ID": "500.0", "PRODUCT_NAME": "500 MB - 30 days (SME)", "PRODUCT_AMOUNT": "337"},
                    {"PRODUCT_CODE": "4", "PRODUCT_ID": "1000.0", "PRODUCT_NAME": "1 GB - 30 days (SME)", "PRODUCT_AMOUNT": "673"},
                    {"PRODUCT_CODE": "5", "PRODUCT_ID": "2000.0", "PRODUCT_NAME": "2 GB - 30 days (SME)", "PRODUCT_AMOUNT": "1346"}
                ]
            }
        ],
        "Glo": [
            {
                "ID": "02",
                "PRODUCT": [
                    {"PRODUCT_CODE": "1", "PRODUCT_ID": "200", "PRODUCT_NAME": "200 MB - 14 days (SME)", "PRODUCT_AMOUNT": "92"},
                    {"PRODUCT_CODE": "2", "PRODUCT_ID": "500", "PRODUCT_NAME": "500 MB - 30 days (SME)", "PRODUCT_AMOUNT": "225"}
                ]
            }
        ]
    }
}

@app.get("/fetch-data")
def fetch_data():
    return data

@app.post('/login',response_model=WalletCreate,status_code = status.HTTP_200_OK)
async def login(username:str,pin:str,db:DBSession):
    query = select(BaseUser).where(BaseUser.username == username)
    result:Result = await db.execute(query)
    user = result.scalars().first()
    if user:
        verify = pwd_context.verify(pin,user.pin)
        if verify:
            return user
    raise HTTPException(status_code =status.HTTP_401_UNAUTHORIZED,detail='User not found')
        
    

            
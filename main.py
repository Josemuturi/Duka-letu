from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Secure-Duka: Enterprise Edition")

# --- SECURITY CONFIGURATION ---
SECRET_KEY = "microsoft-adc-nairobi-2026" 
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock User Data (Modeled after a Duka Owner)
fake_users_db = {
    "admin": {"username": "admin", "password": "securepassword123"}
}

# Your Functional Inventory Data (Populated)
inventory  = [
   {"item": "Maize Flour", "price": 120, "unit": "KES/kg"},
   {"item": "White Rice", "price": 150, "unit": "KES/kg"},
   {"item": "Cooking Oil", "price": 200, "unit": "KES/liter"},
]

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid Credentials")
        return username
    except:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# --- PROTECTED ENDPOINTS ---

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or form_data.password!= user["password"]:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/inventory")
async def get_inventory(current_user: str = Depends(get_current_user)):
    # Only logged-in users can see this now!
    return inventory

@app.get("/predict-stockouts")
async def predict_stockouts(current_user: str = Depends(get_current_user)):
    # Data Science layer protected by the Security Shield
    at_risk = [item for item in inventory if item["stock"] < 5]
    return {
        "analysis": "Predictive Stock Alert",
        "at_risk_items": at_risk,
        "authorized_by": current_user
    }
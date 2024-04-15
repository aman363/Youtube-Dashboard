from fastapi import FastAPI, File, UploadFile
from typing import Union
import json
import os
import pandas as pd

app = FastAPI()

csv_dir = os.getcwd()+'/csv_file/'
df_yr = pd.read_csv(csv_dir+'info_yr.csv',encoding='utf_8_sig',index_col=0)
df_yr_dlc = pd.read_csv(csv_dir+'info_yr_dlc.csv',encoding='utf_8_sig',index_col=0)
df_yr_misc = pd.read_csv(csv_dir+'info_misc_yr.csv',encoding='utf_8_sig',index_col=0)
df_api_rep = pd.read_csv(csv_dir+'api_rep.csv',encoding='utf_8_sig',index_col=0)
df_top5Watch = pd.read_csv(csv_dir+'TOP5_watch.csv',encoding='utf_8_sig',index_col=0)

@app.get("/")
async def root():
    return {"message": "Hello World"}

def info_yr():
    res = df_yr.to_json(orient="records")
    parsed = json.loads(res)
    return parsed
@app.get("/yr")
async def load_csv():
    return info_yr()

def info_yr_dlc():
    res = df_yr_dlc.to_json(orient="records")
    parsed = json.loads(res)
    return parsed
@app.get("/yrdlc")
async def load_csv():
    return info_yr_dlc()

def miscinfo():
    res = df_yr_misc.to_json(orient="records")
    parsed = json.loads(res)
    return parsed
@app.get("/miscinfo")
async def load_csv():
    return miscinfo()

def statrank():
    res = df_api_rep.to_json(orient="records")
    parsed = json.loads(res)
    return parsed
@app.get("/statrank")
async def load_csv():
    return statrank()

@app.get("/top5")
async def top5():
    return df_top5Watch




import asyncio
import pandas as pd
from io import BytesIO
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from httpx import AsyncClient

app = FastAPI()

@app.get("/export")
async def export():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df = pd.DataFrame([{"A": 1, "B": 2}])
        df.to_excel(writer, sheet_name="Sheet1", index=False)
            
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

async def test():
    async with AsyncClient(app=app, base_url="http://test") as client:
        try:
            response = await client.get("/export")
            print("Status:", response.status_code)
            print("Headers:", response.headers)
            print("Content length:", len(response.content))
        except Exception as e:
            print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(test())

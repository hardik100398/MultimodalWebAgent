from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.oai_agent.oai_agent import run_process
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json


app = FastAPI()


html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multimodal Web Agent</title>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {
            const ws = new WebSocket('ws://' + location.host + '/ws');
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                document.getElementById('response').innerText = message.data;
            };

            document.getElementById('prompt-form').addEventListener('submit', function(e) {
                e.preventDefault();
                const prompt = document.getElementById('prompt-input').value;
                ws.send(JSON.stringify({data: prompt}));
            });
        });
    </script>
</head>
<body>
    <div style="display: flex;">
        <div style="width: 50%;">
            <form id="prompt-form">
                <input type="text" id="prompt-input" placeholder="Type your prompt here">
                <button type="submit">Send</button>
            </form>
            <div id="response"></div>
        </div>
        <div style="width: 50%;">
            <iframe src="about:blank" id="browser-frame" style="width: 100%; height: 100vh;"></iframe>
        </div>
    </div>
</body>
</html>
"""


@app.get("/")
async def read_root():
    return {"message":"Welcome to Multimodal agent API"} 

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        data_json = json.loads(data)
        prompt = data_json['data']
        # Process the prompt here
        response = f"Processed: {prompt}"
        await websocket.send_text(json.dumps({'data': response}))

@app.post("/start_browser")
async def start_browser(url: str):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return {"status": "browser started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
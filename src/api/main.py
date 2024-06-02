from fastapi import FastAPI, Form, WebSocket
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import openai
import logging
import json
import asyncio
from src.oai_agent.oai_agent import run_process


app = FastAPI()


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    global playwright, browser, page
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()


@app.on_event("shutdown")
async def shutdown_event():
    await page.close()
    await browser.close()
    await playwright.stop()


@app.get("/", response_class=HTMLResponse)
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI with WebSocket</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                height: 100vh;
                margin: 0;
            }
            .sidebar {
                width: 250px;
                background-color: #f1f1f1;
                padding: 15px;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }
            .content {
                flex: 1;
                padding: 15px;
            }
            .button {
                display: block;
                width: 100%;
                padding: 10px;
                margin: 5px 0;
                background-color: #fff;
                border: 1px solid #ddd;
                text-align: left;
                cursor: pointer;
            }
            iframe {
                width: 100%;
                height: calc(100vh - 30px);
                border: none;
            }
        </style>
        <script>
            let socket;
            function connectWebSocket() {
                socket = new WebSocket("ws://localhost:8000/ws");
                socket.onmessage = function(event) {
                    const iframe = document.getElementById("iframeContent");
                    iframe.srcdoc = event.data;
                };
            }

            async function sendPrompt(prompt) {
                const response = await fetch('/prompt', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'prompt=' + encodeURIComponent(prompt)
                });
            }

            window.onload = connectWebSocket;
            function startTask() {
            sendPrompt("TASK: Go to the Amazon website and search for a laptop, filter for laptops with more than 4 stars, select the first and put it in the cart. 1. Go to the website https://www.amazon.com using the \'read_url\'. 2. Search for \'laptop\' using the \'input_text\'. 3. Click on the more than 4 stars filter using the \'click_element\'. 4. Click on the first product using the \'click_element\'. 5. Add the item to the cart by clicking on the \'Add to Cart\' button using the \'click_element\'. Write \'TERMINATE\' to end the conversation.");
            }
        </script>
    </head>
    <body>
        <div class="sidebar">
            <button class="button" onclick="startTask()">Start Task</button>
        </div>
        <div class="content">
            <iframe id="iframeContent" src="" title="Iframe Example"></iframe>
        </div>
    </body>
    </html>
    """
    return html_content


@app.post("/prompt")
async def handle_prompt(prompt: str = Form(...)):
    try:
        asyncio.create_task(run_task(prompt))
        return {"status": "Prompt received"}
    except Exception as e:
        print(e)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        manager.disconnect(websocket)


async def send_page_content():
    content = await page.content()
    await manager.send_message(content)


async def run_task(prompt: str):
    try:
        # Use OpenAI API to process the prompt
        response = await run_process(prompt)
        # Parse the response to get the steps
        steps = response.chat_history

        for i in steps:
            await send_page_content()  # Send updated content to WebSocket clients

        await manager.send_message("TERMINATE")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

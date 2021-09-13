
from flask import Flask
from flask import request
import json
import math
import random

app = Flask(__name__)

# CONSTANTS
def WIDTH():
    return 800
def HEIGHT():
    return 600
def PADDLE_WIDTH():
    return 22
def PADDLE_HEIGHT():
    return 92
def VELOCITY():
    return 2
def LOSE_CODE():
    return "<html><body><h1>YOU LOST!!</h1></body></html>"
def PLAYER_DISTANCE():
    return 20

def getAngleSin(val):
    angle = math.sin(val) * 2 - 1
    if angle <= 0:
        angle -= 10
    else:
        angle += 10
    return angle

def getAngleCos(val):
    angle = math.cos(val) * 2 - 1
    angle *= VELOCITY()
    if angle <= 0:
        angle -= 10
    else:
        angle += 10
    return angle

def constructStartState():
    return constructFirstFrame(400, 300, getAngleSin(random.randint(0, 6)), getAngleCos(random.randint(0, 6)), 254)

def calculateRebound(paddleY, ballY, isRight):
    theta = (((ballY - paddleY)/PADDLE_HEIGHT()) * 2 * math.pi)
    ballXVelocity = abs(getAngleCos(theta))
    ballYVelocity = -1 * getAngleSin(theta)
    ballXVelocity *= -1 if isRight else 1
    return (ballXVelocity, ballYVelocity)

@app.route('/')
def start():
    return constructStartState()

@app.route('/render-frame', methods=['POST'])
def compute():
    data = json.loads(request.data)
    control = data["control"]
    ballX = math.floor(float(data["ballX"]))
    ballY = math.floor(float(data["ballY"]))
    ballVY = math.floor(float(data["ballVY"]))
    ballVX = math.floor(float(data["ballVX"]))
    paddleY = int(data["paddleY"])
    if control == "up":
        paddleY -= PLAYER_DISTANCE()
    elif control == "down":
        paddleY += PLAYER_DISTANCE()
    else:
        if ballX <= PADDLE_WIDTH() or ballX >= WIDTH() - PADDLE_WIDTH() or ballY <= 0 or ballY >= HEIGHT():
            ballVY = -1 * ballVY
            if ballX <= PADDLE_WIDTH():
                ballX += 14
                if ballY <= paddleY or ballY >= paddleY + PADDLE_HEIGHT():
                    return LOSE_CODE()
                else:
                    ballVX, ballVY = calculateRebound(paddleY, ballY, ballX > WIDTH() / 2)
            if ballX >= WIDTH() - PADDLE_WIDTH():
                ballX -= 14
                if ballY <= paddleY or ballY >= paddleY + PADDLE_HEIGHT():
                    return LOSE_CODE()
                else:
                    ballVX, ballVY = calculateRebound(paddleY, ballY, ballX > WIDTH() / 2)
            if ballY <= 0:
                ballY += 14
                ballVY = 1 * ballVY
            if ballY >= HEIGHT() - 14:
                ballY -= 14
                ballVY = 1 * ballVY

        ballX += ballVX
        ballY += ballVY

    return constructFrame(ballX, ballY, ballVX, ballVY, paddleY)

def constructFrame(ballX, ballY, ballVX, ballVY, paddleY):
    return f"""<body>
                    <div style="border: 2px solid black;display:inline-block;">
                    <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                        <g>
                        <title>Game Layer</title>
                        <rect id="paddle1" height="92" width="22" y="{str(paddleY)}" x="0" stroke="#000" fill="#000000"/>
                        <rect id="paddle2" height="92" width="22" y="{str(paddleY)}" x="778" stroke="#000" fill="#000000"/>
                        <ellipse ry="14" rx="14" id="svg_3" cy="{str(ballY)}" cx="{str(ballX)}" stroke="#000" fill="#000000"/>
                        </g>
                    </svg>
                    </div>
                    <p id="ballX" style="display:none">{str(ballX)}</p>
                    <p id="ballY" style="display:none">{str(ballY)}</p>
                    <p id="ballVX" style="display:none">{str(ballVX)}</p>
                    <p id="ballVY" style="display:none">{str(ballVY)}</p>
                    <p id="paddleY" style="display:none">{str(paddleY)}</p>
             </body>"""

def constructFirstFrame(ballX, ballY, ballVX, ballVY, paddleY):
    return f"""<html>
                    <body>
                        <div style="border: 2px solid black; display:inline-block;">
                        <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
                            <g>
                            <title>Game Layer</title>
                            <rect id="paddle1" height="92" width="22" y="{str(paddleY)}" x="0" stroke="#000" fill="#000000"/>
                            <rect id="paddle2" height="92" width="22" y="{str(paddleY)}" x="778" stroke="#000" fill="#000000"/>
                            <ellipse ry="14" rx="14" id="svg_3" cy="{str(ballY)}" cx="{str(ballX)}" stroke="#000" fill="#000000"/>
                            </g>
                        </svg>
                        </div>
                        <p id="ballX" style="display:none">{str(ballX)}</p>
                        <p id="ballY" style="display:none">{str(ballY)}</p>
                        <p id="ballVX" style="display:none">{str(ballVX)}</p>
                        <p id="ballVY" style="display:none">{str(ballVY)}</p>
                        <p id="paddleY" style="display:none">{str(paddleY)}</p>
                    </body>
                    <script>
                        function v(id) {{
                            return document.getElementById(id).innerHTML;
                        }}
                        document.addEventListener('keydown', logKey);

                        window.addEventListener('DOMContentLoaded', (event) => {{
                            setInterval(function() {{renderNextFrame("", v("ballX"), v("ballY"), v("ballVX"), v("ballVY"), v("paddleY"));}}, 300);
                        }});

                        function logKey(e) {{
                            if (e.keyCode == 38) {{
                                // PADDLE UP
                                renderNextFrame("up", v("ballX"), v("ballY"), v("ballVX"), v("ballVY"), v("paddleY"));
                            }} else if (e.keyCode == 40) {{
                                // PADDLE DOWN
                                renderNextFrame("down", v("ballX"), v("ballY"), v("ballVX"), v("ballVY"), v("paddleY"));
                            }}
                        }}

                        function renderNextFrame(control, ballX, ballY, ballVX, ballVY, paddleY) {{
                            data = {{"control": control, "ballX": ballX, "ballY": ballY, "ballVX": ballVX, "ballVY": ballVY, "paddleY": paddleY}};
                            fetch("/render-frame", {{method: "POST", body: JSON.stringify(data)}}).then((data) => data.text()).then((text) => {{console.log("Hi"); document.body.innerHTML = text;}});
                        }}
                    </script>
                </html>"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

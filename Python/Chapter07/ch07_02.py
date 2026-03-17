"""
    제작 시간 : 0317_12:25
    유형 : 예제
    주제 : 
    문제 설명 : 
    - 
"""

# 기본 모듈
import sys

from urllib import request

from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    word = """
    <h1>Hello World</h1>
    <h2>만나서 반갑수</h2>
    """
    
    return word
def main() -> None:
    hello()



if __name__ == "__main__":
    main()
    app.run(host="0.0.0.0", port=5000, debug=True)
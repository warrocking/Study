# VSCode + Remote Jupyter Setup

## 1) Install extensions in VSCode
- Python (`ms-python.python`)
- Jupyter (`ms-toolsai.jupyter`)

## 2) Connect to your Jupyter server
1. Open Command Palette (`Ctrl+Shift+P`)
2. Run `Jupyter: Specify Jupyter Server for Connections`
3. Choose `Existing`
4. Paste server URL:
   - `http://192.168.101.101:8888/?token=YOUR_TOKEN`

## 3) Open notebook and run with Shift+Enter
1. Open or create `.ipynb` file in VSCode
2. Select kernel from the connected server
3. Run each cell with `Shift+Enter`

## 4) Quick connection test cell
```python
import pop
print("pop import ok")
```

## 5) If connection fails
- Confirm VSCode PC can reach `192.168.101.101:8888`
- Confirm token is valid
- On server terminal, check token with:
  - `jupyter server list`

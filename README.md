
'''
uv venv
source .venv/bin/activate  
uv pip install -r requirements.txt
// uv pip install 'mcp[cli]'

uv run mcp dev morphogen_mcp.py

// Claude Desktop에 재설치하는 방법
mcp install morphogen_mcp.py --name "morphogen" -f .env

// 개발 중이라면 dev 모드로 실행하기
mcp dev morphogen_mcp.py --with-editable .
mcp dev morphogen_mcp.py
'''
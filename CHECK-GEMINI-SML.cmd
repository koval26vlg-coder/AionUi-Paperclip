@echo off
cd /d D:\AionUi-Paperclip
echo Gemini MCP servers:
gemini mcp list
echo.
echo Running Gemini SML smoke-test...
gemini -p "Проведи smoke-test MCP SML: вызови sml.ping, затем кратко ответь по-русски, работает ли доступ к общей памяти SML." --allowed-mcp-server-names sml --approval-mode yolo --skip-trust --output-format text
pause

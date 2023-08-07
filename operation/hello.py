import fortune
def bot_hello(ast = True):
    query_data = '你好，我是LenoMate'
    
    if ast:
        "星座运势"
        ast = fortune.query()
        ast_query = ast.constellation()
        if ast_query: query_data += '\n您的今日运势为:\n'+ast_query + '请问有什么可以帮您'
        
    hello = {'chat':query_data,'command':'START msegde.exe http://localhost:8081/'}
    return hello
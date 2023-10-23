import operation.fortune as fortune


class bot_hello:
    def __init__(self,system = 'Windows',language='ch') -> None:
        self.language = language
        self.query_data = '你好，我是LenoMate。Building Bridges, one byte at a time.' if language == 'cn' else 'Hello, I am LenoMate. Building Bridges, one byte at a time.'
        self.system = system

    def hello(self, ast=True):

        if ast:
            "星座运势"
            ast = fortune.query()
            ast_query = ast.constellation()
            if ast_query: self.query_data += '\n您的今日运势为:\n'+ast_query 
        
        self.query_data += '请问有什么可以帮您?' if self.language == 'cn' else 'What can I do for you? '
        hello = {'chat':self.query_data,
                 'command':"os.system('START msedge.exe http://localhost:8081/')" if self.system == 'Windows' else "os.system('open -a Safari.app http://localhost:8081/')"
                 }
        return hello

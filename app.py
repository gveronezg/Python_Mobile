import os, sqlite3, toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

class Pythonando(toga.App):
    def startup(self):
        # Obtém o caminho do diretório de dados da aplicação
        data_dir = self.paths.app
        # Constroi o caminho completo para o arquivo de banco de dados
        db_path = os.path.join(data_dir, 'pedidosMobile.db')

        # Criar a conexão com o banco de dados SQLite
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Criar a tabela pedidos, caso não exista
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendedor TEXT,
            produto TEXT,
            quantidade INTEGER,
            total REAL)
        ''')
        
        # Criar a interface
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # Adicionando elementos
        main_box.add(toga.Label('Vendedor(a):'))
        self.vendido_por = toga.TextInput(placeholder='Vendido por...')
        main_box.add(self.vendido_por)
        '''
        self.senha = toga.PasswordInput(placeholder='Senha...')
        main_box.add(self.senha)
        '''
        main_box.add(toga.Label('Produto:'))
        self.produtos_precos = {
            'Sapato': 200,
            'Carteira': 90,
            'Cinto': 50
        }
        self.produto = toga.Selection(items=list(self.produtos_precos.keys()))
        main_box.add(self.produto)

        main_box.add(toga.Label('Quantidade:'))
        self.quantidade = toga.NumberInput(min_value=1)
        main_box.add(self.quantidade)

        main_box.add(
            toga.Button('Registrar Pedido', on_press=self.registrar)
        )

        # Campo para mostrar os registros do banco de dados
        self.registros_text = toga.MultilineTextInput(readonly=True, style=Pack(height=200))
        main_box.add(self.registros_text)

        # Atualizar registros ao iniciar o aplicativo
        self.atualizar_registros()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def registrar(self, widget):
        # Obter dados do pedido
        vendedor = self.vendido_por.value
        produto = self.produto.value
        valor = self.produtos_precos.get(produto, 0)
        quantidade = int(self.quantidade.value)
        total = valor * quantidade

        # Inserir o pedido no banco de dados
        try:
            self.cursor.execute('''INSERT INTO pedidos (vendedor, produto, quantidade, total) VALUES (?, ?, ?, ?)''', (vendedor, produto, quantidade, total))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao inserir no banco de dados: {e}")

        # Mostrar a confirmação do pedido
        self.main_window.info_dialog(
            'Pedido Registrado',
            f'''Dados do Pedido:
            Quantidade: {quantidade}
            Produto: {produto}
            Vendedor(a): {vendedor}
            Total: R$ {total:.2f}
            '''
        )

        # Atualizar a interface
        finalizado = toga.Box(style=Pack(direction=COLUMN))
        finalizado.add(
            toga.Label('Pedido Registrado!\nAgradecemos a preferência.')
        )
        self.main_window.content = finalizado

    def atualizar_registros(self):
        # Consultar e mostrar os registros no banco de dados
        try:
            self.cursor.execute("SELECT vendedor, produto, quantidade, total FROM pedidos")
            registros = self.cursor.fetchall()
            
            if registros:
                texto_registros = "\n".join(
                    [f"{vendedor} - {produto} - {quantidade} - R$ {total:.2f}" for vendedor, produto, quantidade, total in registros]
                )
                self.registros_text.value = texto_registros
            else:
                self.registros_text.value = "Nenhum registro encontrado."
        
        except sqlite3.Error as e:
            print(f"Erro ao consultar registros: {e}")

    def on_exit(self):
        # Fechar a conexão com o banco de dados ao fechar o aplicativo
        self.conn.close()

def main():
    return Pythonando('PedidoApp', 'org.beeware.pedidoapp')

if __name__ == '__main__':
    main().main_loop()
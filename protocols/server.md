### Objetivo
---

- Definir como a comunicação e o cliente e o servidor deve acontecer.

> [!NOTE]
> a arquitetura desejada é uma Peer-to-Peer híbrida, porém para que seja híbrida o servidor serve apenas
> para auxiliar que clientes conectem entre si, mas isso pode resultar em erros por conta do NAT(?)
> Necessita investigação.
<br>

### Mensagens
---
A comunicação com o servidor é feita através de mensagens no formato:

    tipo:arg1;argN

Onde:
`tipo` é o tipo da mensagem, ver tabela abaixo.
`arg1` é o primeiro argumento da lista de argumentos.
`argN` é o último argumento da lista de argumentos.


#### Mensagens aceitas
| Tipo | Argumentos | Descrição |
| :-: | :-: | :-- |
| `REGISTER` | `nome do jogador` | registra o cliente no servidor |
| `UNREGISTER` | `nome do jogador` | remove o cliente do servidor |
| `ROOM` | `priv\|pub`;`nome da sala`;`<senha>` | cria uma sala (`priv`: privada onde nesse caso requer a senha, `pub`: pública erro se receber senha) |
| `CROOM` | `nenhum` | o cliente, dono da sala, informa que não aceita mais clientes pois começará a partida (sala fechada) |
| `LIST` | `<priv\|pub>` | lista as salas (`priv`: apenas privadas, `pub`: apenas públicas) |
| `ENTER` | `código da sala`;`<senha>` | entra em uma sala |
| `LEAVE` | `nenhum` | sai da sala |
| `STATUS` | `nenhum` | estado atual da sala qual o cliente está |

> [!NOTE]
> * argumentos entre os sinais `<` e `>` são argumentos opcionais.
> * o sinal `|` quer dizer que é um valor ou o outro valor
<br>

### Respostas
---
#### `REGISTER`
**Sucesso**
- OK

**Falha**
1. Nome de jogador inválido
2. Número de argumentos inválido
3. Jogador já registrado

#### `UNREGISTER`
**Sucesso**
- OK

**Falha**
1. Cliente não registrado
2. Número de argumentos inválido

#### `ROOM`
**Sucesso**
- Código da sala

**Falha**
1. Tipo da sala inválido
2. Senha não fornecida para sala privada
4. Sala pública não requer senha
5. Nome da sala inválido
6. Cliente não registrado
7. Número de argumentos inválido

#### `CROOM`
**Sucesso**
- OK

**Falha**
1. Cliente não está em nenhuma sala
2. Cliente não registrado
3. Número de argumentos inválido
4. Somente o dono da sala pode fechá-la
5. Número de clientes insuficiente na sala

#### `LIST`
**Sucesso**
- Uma lista contendo as entradas separadas pelo caractere `\n` e os valores por `,`:
  - tipo da sala
  - nome da sala
  - código da sala
  - número de jogadores
  - número máximo de jogadores

**Falha**
1. Tipo da sala inválido
2. Cliente não registrado
3. Número de argumentos inválido

#### `ENTER`
**Sucesso**
- OK

**Falha**
1. Código da sala inválido
2. Senha da sala está incorreta
3. Senha não fornecida
5. Cliente já está na sala
6. Cliente já está em outra sala
8. Cliente não registrado
9. Número de argumentos inválido

#### `LEAVE`
**Sucesso**
- OK

**Falha**
1. Cliente não está em nenhuma sala
2. Cliente não registrado
3. Número de argumentos inválido

#### `STATUS`
**Sucesso**
- Os valores abaixo separados por vírgula:
  - tipo da sala
  - nome da sala
  - código da sala
  - número de jogadores
  - número máximo de jogadores

**Falha**
1. Cliente não está em nenhuma sala
2. Cliente não registrado
3. Número de argumentos inválido
<br>

### Comportamento
---
#### Registar um cliente
Processo onde o cliente informa ao servidor a sua existência, também serve como teste de conexão
com o servidor.

**Gatilho**
- receber do cliente a mensagem `REGISTER`

**Ação**
- criar um registro do cliente como nome, endereço (IP) e porta
<br>


#### Fechamento da sala
O fechamento da sala é quando a sala está completa, com todos os jogadores, ou quando solicitado
pelo dono da sala que ela seja fechada para que comece a partida.

Uma sala fechada é excluída pois o gerenciamento do jogo passará para o cliente dono da sala. O
primeiro cliente na lista de clientes é considerado o dono, para efeitos práticos o cliente a criar
a sala é o primeiro cliente na lista de clientes, por isso é considerado o dono da sala, caso ele saía,
outro cliente que entrou imediatamente após a criação da sala ele considerado o dono.

A mensagem `CROOM` só é obedecida caso a sala tenha no mínimo dois clientes conectados.

**Gatilho**
- o servidor identifica que o número máximo de jogadores foi atingido
- o cliente envia uma mensagem (`CROOM`) ao servidor solicitando o fechamento

**Ação**
- enviar uma mensagem (`PLAY`) aos clientes da sala informando que a partida começará e quem é o
  cliente host
- envia uma mensagem (`GAME`) ao cliente dono da sala para que comece a partida
- remove do servidor a sala e todos os clientes conectados a sala
<br>

#### Entrar na sala
Fazer com que um cliente se conecte a outros clientes através de uma sala.

**Gatilho**
- receber do cliente a mensagem `ENTER`

**Ação**
- enviar para todos cliente uma mensagem (`CONNECT`) informando que ele deve se conectar ao novo cliente.
<br>

#### Sair da sala
Um cliente solicita ao servidor que seja removido da sala

**Gatilho**
- receber do cliente a mensagem `LEAVE`

**Ação**
- remover o cliente da sala
- notificar os outros clientes da sala que um cliente saiu enviado a mensagem `DISCONNECT`


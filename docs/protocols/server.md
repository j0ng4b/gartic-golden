### Objetivo
---

- Definir como a comunicação e o cliente e o servidor deve acontecer.
- Ser um túnel/proxy de comunicação entre os clientes.

> [!NOTE]
> ~a arquitetura desejada é uma Peer-to-Peer híbrida, porém para que seja híbrida o servidor serve apenas
> para auxiliar que clientes conectem entre si, mas isso pode resultar em erros por conta do NAT(?)
> Necessita investigação.~
> 
> usando o servidor como túnel porque não é possível ser híbrido, não um híbrido onde o servidor so server
> para a primeira etapa da comunicação que é identificar outros clientes.
<br>

### Mensagens
---
A comunicação com o servidor é feita através de mensagens no formato:

    cliente/tipo:arg1;argN

Onde:
- `cliente` é o cliente para qual a mensagem deve ser repassada.
- `tipo` é o tipo da mensagem, ver tabela abaixo.
- `arg1` é o primeiro argumento da lista de argumentos.
- `argN` é o último argumento da lista de argumentos.

> [!NOTE]
> o campo `cliente` pode ser vazio o que faz com que o servidor interprete a mensagem como sendo direcionada
> para ele.
> >
> exemplo:
> ```
> /REGISTER:Shrek
> ```


#### Mensagens aceitas
| Tipo | Argumentos | Descrição |
| :-: | :-: | :-- |
| `REGISTER` | `nome do jogador` | registra o cliente no servidor |
| `UNREGISTER` |  | remove o cliente do servidor |
| `ROOM` | `priv\|pub`;`nome da sala`;`tema`;`<senha>` | cria uma sala (`priv`: privada onde nesse caso requer a senha, `pub`: pública erro se receber senha) |
| `CROOM` |  | o cliente, dono da sala, informa que não aceita mais clientes pois começará a partida (sala fechada) |
| `LIST` | `<priv\|pub>` | lista as salas (`priv`: apenas privadas, `pub`: apenas públicas) |
| `ENTER` | `código da sala`;`<senha>` | entra em uma sala |
| `LEAVE` |  | sai da sala |
| `END` |  | apaga a sala ao qual o cliente está |

> [!TIP]
> * argumentos entre os sinais `<` e `>` são argumentos opcionais.
> * o sinal `|` quer dizer que é um valor ou o outro valor
<br>

### Respostas
---
> [!IMPORTANT]
> *Respostas padrão para todas mensagens*
> 
> **Falha**
> 1. Cliente não registrado  
>    *(exceto para `REGISTER` e `LIST`)*
> 
> 2. Número de argumento inválido

#### `REGISTER`
**Sucesso**
- OK:id do cliente

**Falha**
1. Nome de jogador inválido
2. Jogador já registrado

#### `UNREGISTER`
**Sucesso**
- OK

#### `ROOM`
**Sucesso**
- Código da sala

**Falha**
1. Tipo da sala inválido
2. Senha não fornecida para sala privada
4. Sala pública não requer senha
5. Nome da sala inválido

#### `CROOM`
**Sucesso**
- OK

**Falha**
1. Cliente não está em nenhuma sala
2. Somente o dono da sala pode fechá-la
3. Número de clientes insuficiente na sala
4. Poucos clientes na sala

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

#### `ENTER`
**Sucesso**
- OK

**Falha**
1. Código da sala inválido
2. Senha da sala está incorreta
3. Senha não fornecida
5. Cliente já está na sala
6. Cliente já está em outra sala
7. A sala não está disponível

#### `LEAVE`
**Sucesso**
- OK

**Falha**
1. Cliente não está em nenhuma sala

#### `END`
**Sucesso**
- OK

**Falha**
1. Cliente não está em nenhuma sala
2. Somente o dono da sala pode excluí-la
3. A sala não está em partida

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
<br>

#### Finalizar sala (Excluir)
Ao termino da partida o cliente dono da sala deve informar ao servidor que ele pode excluir a sala, fazendo
isso, o servidor remove todos os dados da sala e notifica outros clientes da sala.

**Gatilho**
- receber do cliente a mensagem `END`

**Ação**
- notificar os clientes que a sala está sendo excluída (`END`)
- efetivamente excluir a sala

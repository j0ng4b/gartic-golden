### Objetivo
---
* Definir como deve acontecer a comunicação entre clientes.
* Definir como a comunicação entre o cliente e o servidor deve acontecer.

> [!NOTE]
> o servidor é usado para indexar os salas e outros clientes porém a comunicação entre clientes
> deve acontecer diretamente, considerando isso, mesmo tendo servidor como super nó talvez haja
> problemas com NAT(?) Necessita investigação.
<br>

### Mensagens
---
A comunicação com o cliente é feita através de mensagens no formato:

    tipo:arg1;argN

Onde:
`tipo` é o tipo da mensagem, ver tabela abaixo.
`arg1` é o primeiro argumento da lista de argumentos.
`argN` é o último argumento da lista de argumentos.


#### Mensagens aceitas (vinda do servidor)
| Tipo | Argumentos | Descrição
| :-: | :-: | :-- |
| `CONNECT` | `endereço do cliente`;`porta do cliente` | o cliente deve iniciar uma "conexão" com outro cliente |
| `DISCONNECT` | `endereço do cliente`;`porta do cliente` | desconecta um cliente |
| `GAME` | `nenhum` | iniciar a partida |
| `PLAY` | `endereço do cliente`;`porta do cliente` | informa que começará a partida e quem é o host |

#### Mensagens aceitas (vinda de outro cliente)
| Tipo | Argumentos | Descrição
| :-: | :-: | :-- |
| `GREET` | `nenhum` | cumprimenta outro cliente |
| `DRAW` | `endereço do cliente`;`porta do cliente` | é a vez do cliente desenhar |
| `FDRAW` | `pontuação` | encerrou a vez do cliente desenhar |
| `GUESS` | `objeto` | enviar palpite do cliente |
| `GTRA` | `endereço do cliente`;`porta do cliente` | o cliente acertou a resposta |
| `SKIP` | `nenhum` | não dar mais palpites |
| `CHAT` | `mensagem` | enviar mensagem de texto |
| `CANVAS` | `desenho` | enviar o desenho |
| `SCORE` | `nenhum` | solicita o sua pontuação de acordo com o outro cliente |


> **NOTA**
> * argumentos entre os sinais `<` e `>` são argumentos opcionais.
> * o sinal `|` quer dizer que é um valor ou o outro valor
<br>

### Respostas
---
#### `CONNECT`
*sem resposta*

#### `DISCONNECT`
*sem resposta*

#### `GAME`
*sem resposta*

#### `PLAY`
**Sucesso**
- `READY` que significa pronto para iniciar a partida
- `LEAVY` que informa que o cliente deseja deixar a sala

<br>

#### `GREET`
**Sucesso**
- nome do cliente

#### `DRAW`
*sem resposta*

#### `FDRAW`
*sem resposta*

#### `GUESS`
**Sucesso**
- OK

**Falha**
- Palavra incorreta

#### `GTRA`
*sem resposta*

#### `SKIP`
*sem resposta*

#### `CHAT`
*sem resposta*

#### `SCORE`
**Sucesso**
- a pontuação atualizada do cliente que solicitou

<br>

### Comportamento
---
#### Iniciar jogo
O cliente dono da sala recebe a mensagem `GAME` informando que ele deve começar a partida.
Outros clientes recebem a mensagem `PLAY` informando quem é o dono da sala.

Etapas:
- gerar a ordem de quem desenhará (host)
- informar aos clientes quem desenhará átraves da mensagem `DRAW` (host)
- solicita sua pontuação atual aos outros clientes apos receber o `DRAW`
- manter o *timeout* de quem desenha (host)
- manter a lista de clientes que acertaram o desenho ou que não vão dar mais palpites
- quando atingir o *timeout* informar ao cliente que está desenhando que ele deve parar de
  desenhar `FDRAW` (host)

A pontuação de um cliente é a moda (mais alta) dos valores recebidos

**Gatilho**
- receber do servidor ou `GAME` ou `PLAY`
<br>

#### Conectar a outro cliente
Quando o cliente deve se conectar com outro cliente ele envia uma mensagem (`GREET`) para tanto 
testar a conexão entre eles quanto obter o nome do outro cliente.

**Gatilho**
- receber do servidor a mensagem (`CONNECT`) para se conectar a outro cliente

**Ação**
- envia uma mensagem (`GREET`) para o outro cliente
<br>

#### Desconectar de outro cliente
Não é mais necessário se comunicar com outro cliente

**Gatilho**
- receber do servidor a mensagem `DISCONNECT`

**Ação**
- remove o registro do cliente, "se desconectando"
<br>

#### Palpite
Um cliente informa a outro cliente, que está desenhando, o seu palpite, e espera a validação se
esta correto.

**Gatilho**
- receber de outro cliente a mensagem `GUESS`

**Ação**
- validar se o palpite corresponde a palavra/frase tema do desenho
- notificar os clientes da sala se o cliente acertou
<br>

#### Desenho
O cliente dono da sala que gerencia a ordem de quem desenha, ele também deve manter uma lista
de quem falta dar palpite (ou que não quis mais dar palpite), ao final quando todos tiverem
palpitado ele informa ao cliente que atualmente está desenhando a sua pontuação e que não desenha
mais.

Caso que esteja desenhando é o dono da sala, ele não precisa enviar mensagem para si mesmo.

**Ação**
- ao início notificar (`DRAW`) um cliente que ele será quem faz o desenho
- ao final notificar (`FDRAW`) o cliente que ele não desenhará mais
<br>

#### Transmissão do desenho
O cliente que está atualmente desenhando deve frequentemente transmitir os dados da tela de desenho
para que outros clientes fiquem atualizados com o estado do desenho.

Os dados da tela de desenho devem seguir os seguintes passos para facilitar a transmissão e
economizar na quantidade de dados transmitidos:
- comprimir os dados da tela (usando zlib por exemplo)
- codificar os dados da tela para base64

**Gatilho**
- ao final de cada atualização de janela

**Ação**
- enviar os dados da tela para os outros clientes

### Objetivo
---
* Definir como deve acontecer a comunicação entre clientes.
* Definir como a comunicação entre o cliente e o servidor deve acontecer.

> [!NOTE]
> ~a arquitetura desejada é uma Peer-to-Peer híbrida, porém para que seja híbrida o servidor serve apenas
> para auxiliar que clientes conectem entre si, mas isso pode resultar em erros por conta do NAT(?)
> Necessita investigação.~
> 
> usando o servidor como túnel porque não é possível usá-lo como híbrido, ou seja, o servidor recebe mensagens
> e repassa para outros clientes.
<br>

### Mensagens
---
A comunicação com o cliente é feita através de mensagens no formato:

    cliente/tipo:arg1;argN

Onde:
- `cliente` é o cliente para qual deve se enviar a resposta.
- `tipo` é o tipo da mensagem, ver tabela abaixo.
- `arg1` é o primeiro argumento da lista de argumentos.
- `argN` é o último argumento da lista de argumentos.

> [!IMPORTANT]
> o campo `cliente` pode ser vazio o que significa que o servidor que pode estar esperando uma resposta.
> 
> exemplo:
> ```
> /CONNECT:
> ```


#### Mensagens aceitas (vinda do servidor)
| Tipo | Argumentos | Descrição
| :-: | :-: | :-- |
| `CONNECT` | `id do cliente` | o cliente deve iniciar uma "conexão" com outro cliente |
| `DISCONNECT` | `id do cliente` | desconecta um cliente |
| `GAME` |  | iniciar a partida |
| `PLAY` | `id do cliente` | informa que começará a partida e quem é o host |
| `END` | | informar que a partida está encerrada |

#### Mensagens aceitas (vinda de outro cliente)
| Tipo | Argumentos | Descrição
| :-: | :-: | :-- |
| `GREET` |  | cumprimenta outro cliente |
| `DRAW` | `id do cliente` | é a vez do cliente desenhar |
| `FDRAW` |  | encerrou a vez do cliente desenhar |
| `GUESS` | `objeto` | enviar palpite do cliente |
| `GTRA` | `id do cliente` | o cliente acertou a resposta |
| `SKIP` |  | não dar mais palpites |
| `CHAT` | `mensagem` | enviar mensagem de texto |
| `CANVAS` | `desenho` | enviar o desenho |
| `SCORE` |  | solicita o sua pontuação de acordo com o outro cliente |


> [!TIP]
> * argumentos entre os sinais `<` e `>` são argumentos opcionais.
> * o sinal `|` quer dizer que é um valor ou o outro valor
<br>

### Respostas
---
> [!IMPORTANT]
>  Mensagens sem respostas não serão listadas.

#### `GREET`
**Sucesso**
- nome do cliente

#### `DRAW`
**Sucesso**
- OK

**Falha**
- Cliente não encontrado na partida
- Cliente já acertou o palpite

#### `GUESS`
**Sucesso**
- OK

**Falha**
- Palpite está incorreto
- Palpite já foi dado
- Cliente não encontrado na partida
- Cliente não pode mais dar palpites
- Cliente é quem está desenhando

#### `GTRA`
**Sucesso**
- OK

**Falha**
- Cliente não encontrado na partida
- Cliente já acertou o palpite
- Cliente não pode mais dar palpites
- Cliente é quem está desenhando

#### `SKIP`
**Sucesso**
- OK

**Falha**
- Cliente não encontrado na partida
- Cliente já acertou o palpite
- Cliente já não pode mais dar palpites
- Cliente é quem está desenhando

#### `SCORE`
**Sucesso**
- a pontuação atualizada do cliente que solicitou

**Falha**
- Cliente não encontrado na partida

<br>

### Comportamento
---
#### Iniciar jogo
O cliente dono da sala (chamado host) recebe a mensagem `GAME` informando que ele deve começar
a partida. Outros clientes recebem a mensagem `PLAY` informando quem é o dono da sala e que a
partida começará.

Etapas:
- gerar a ordem de quem desenhará (host)
- informar aos clientes quem desenhará através da mensagem `DRAW` (host)
- manter o *timeout* de quem desenha (host)
- manter a lista de clientes que acertaram o desenho ou que não vão dar mais palpites.  
  *(manter o estado do cliente)*
- quando atingir o *timeout* informar o fim da rodada de desenho com `FDRAW` a todos clientes (host)
- quando todos clientes tiverem dado palpite ou pulado, informar o fim da rodada de desenho com `FDRAW` a todos clientes (host)

**Gatilho**
- receber do servidor ou `GAME` ou `PLAY`
<br>

#### Fim de jogo
Quando todos clientes tiveram desenhado ao menos uma vez o cliente dono da sala pode enviar a
mensagem `END` para o servidor para que ele redistribúa para todos os clientes da sala.

> [!NOTE]
> talvez seja necessário esperar alguns segundos antes de enviar a mensagem `END` para ter certeza
> de que todos clientes conseguiram fazer suas devidas atividades a tempo (ex: atualizar pontuação).

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
- validar se o palpite corresponde ao objeto que deve ser desenhado
- notificar os clientes da sala se o cliente acertou
<br>

#### Desenho
O cliente dono da sala que gerencia a ordem de quem desenha, ele também deve manter uma lista
de quem falta dar palpite (ou que não quis mais dar palpite), ao final quando todos tiverem
palpitado (ou pulado) que a rodada está encerrada ou também caso o timeout tenha sido atingido.

Caso quem esteja desenhando é o dono da sala, ele não precisa enviar mensagem para si mesmo.

**Ação**
- ao início notificar (`DRAW`) a todos clientes o cliente que fara o desenho.
- ao final notificar (`FDRAW`) notificar a todos o fim da rodada.
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
<br>

#### Pontuação
##### Requisitar pontuação
Um cliente sempre ao final de cada rodada solicita sua pontuação enviando a mensagem `SCORE`.

##### Pontuação do cliente
O cliente apenas mantem (modifica, visualiza) a pontuação de outros clientes, a sua própria
pontuação é apenas **somente leitura** no sentido que ele não altera ela quando acerta um desenho
para assim garantir partidas justas.

O cliente atualiza sua própria pontuação através da mensagem `SCORE` enviada para todos outros
clientes que então informam a pontuação do cliente que solicitou. A pontuação final é a moda do
valor mais alto das pontuações, na prática considere as seguintes pontuações:

    20 20 30 30

A pontuação final é 30.  
Motivo:
- moda é 20 e 30 porém 30 é a maior moda.

Dessa forma é garantido que um cliente não forge sua própria pontuação.

##### Pontuação de outros clientes
> [!IMPORTANT]
> Para que não seja necessário sincronização de relógio entre clientes, por hora não haverá pontuação
> baseada no tempo que um cliente levou para acertar o desenho.

O cálculo de pontuação para outros clientes é bem simples, porém existem dois cenários, para quem está
desenhando e quem não está.

O primeiro cenário é para quem está desenhando, esse só recebe pontuação ao final do desenho, seguindo a
seguinte regra:
- Todos acertaram o desenho: 8 pontos
- Apenas alguns acertaram o desenho: 5 pontos
- Tempo esgotado: 0 pontos

Para os demais clientes, as regras são:
- Acertou o desenho: 5 pontos
- Não acertou o desenho no tempo da partida: -3 pontos
- Parou de dar palpite (`SKIP`): 0 pontos

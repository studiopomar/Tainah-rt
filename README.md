<p align="center">
  <img src="assets/tainah.png" alt="Ícone oficial do Tainah" width="192"><br>
  Ícone por <a href="https://youtube.com/@satochi.p">Mori-P</a>
</p>

# Tainah

**Resampler vocal com síntese WORLD para UTAU e OpenUtau.**

O Tainah transforma gravações de voicebanks em notas cantadas, ajustando a altura e
a duração. No Windows, funciona com UTAU clássico e OpenUtau. No macOS e Linux, use
o pacote com OpenUtau.

## Baixar

Os pacotes prontos para uso ficam na página [Versões](../../releases/latest):

- **Windows x64:** `Tainah-LTS-windows-x64.zip`
- **macOS Apple Silicon:** `Tainah-LTS-macos-arm64.zip`
- **Linux x64:** `Tainah-LTS-linux-x64.zip`

Extraia o ZIP do seu sistema e mantenha o executável e a biblioteca na mesma pasta.
No Windows, selecione `Tainah.exe` nas configurações de resampler do UTAU ou do
OpenUtau. No macOS e Linux, coloque `Tainah` na pasta de resamplers do OpenUtau e
selecione-o no modo `CLASSIC`. O arquivo `Tainah.yaml` apresenta as seis flags do
motor no editor de expressões do OpenUtau.

O macOS pode pedir autorização na primeira abertura, pois os pacotes não são
assinados pela Apple. Se isso acontecer, abra **Ajustes do Sistema → Privacidade e
Segurança** e permita a execução do Tainah.

## Tainah-LTS

**LTS** significa *Long Term Support* (suporte de longo prazo). O Tainah alcançou
estabilidade e esta edição terá atualizações no repositório oficial até 2035.
O nome Tainah-LTS identifica essa linha estável de manutenção; os pacotes continuam
compatíveis com UTAU e OpenUtau conforme descrito neste README.

## Recursos

- Analisa a amostra e ressintetiza a voz com WORLD.
- Usa `offset`, `consonant` e `cutoff` recebidos do projeto para respeitar os dados
  de `oto.ini`.
- Mantém o tamanho de saída pedido pelo aplicativo.
- Lê a curva de pitch enviada pelo OpenUtau.
- Oferece as flags `g`, `t`, `B`, `H`, `P` e `C`.
- A flag `P` desloca os formantes sem alterar a nota: valores positivos elevam a
  posição dos formantes e valores negativos a reduzem.
- A flag `C` ajusta o tamanho da região consonantal fixa do `oto.ini`: `C0`
  mantém o valor original, `C-100` desativa essa região e `C100` a duplica. Uma
  região fixa maior reserva mais tempo da nota para o ataque e deixa menos tempo
  elástico para a vogal. Marcadores de loop válidos definem a região fixa e
  prevalecem sobre `C`.
- Mostra um diagnóstico no terminal quando não consegue abrir, analisar ou
  sintetizar a amostra.

Se a análise WORLD falhar, o Tainah retorna um erro.

## Como o resampling funciona

O Tainah usa análise e ressíntese WORLD. Primeiro, analisa o trecho selecionado
do WAV e estima a frequência fundamental com Harvest ou DIO, o envelope espectral
com CheapTrick e a aperiodicidade com D4C. Depois, remapeia esses dados para a
duração pedida, aplica a nota e a curva de pitch, e sintetiza um novo áudio.

O tempo é tratado em regiões. Com espaço suficiente, o ataque e a cauda mantêm
suas durações, e o ajuste de duração se concentra na região sustentada. Se a nota
for curta demais para acomodar essas regiões, ataque e cauda são comprimidos para
caber. Marcadores de loop definem a região sustentada e o marcador de cauda
orienta a parte final. Os valores de `offset`, `consonant` e `cutoff` de `oto.ini`
afetam quais partes da gravação são usadas. O argumento clássico de velocidade é
aceito para compatibilidade, mas atualmente não altera o áudio.

Outros resamplers podem trabalhar diretamente com trechos da onda, alinhando e
sobrepondo segmentos, usar processamento síncrono com o pitch ou combinar métodos.
Essas abordagens e o WORLD têm características diferentes, sem uma técnica que
seja melhor para todos os bancos e frases.

| Aspecto | Tainah com WORLD | Métodos de sobreposição ou síncronos com o pitch |
| --- | --- | --- |
| Operação | Analisa pitch, envelope espectral e aperiodicidade, depois ressintetiza o áudio | Seleciona, alinha, sobrepõe ou repete partes da onda original; o comportamento depende do motor |
| Pitch e duração | Ajustados nos dados da análise antes da síntese | Normalmente tratados pela seleção e sobreposição de segmentos ou pelo alinhamento ao pitch |
| Consoantes | Usa a região fixa de consoante e marcadores opcionais de loop e cauda | Dependem das regras de segmentação e dos dados `oto.ini` |
| Característica | Permite remodelar pitch e duração pelo modelo acústico, mas a análise e a síntese também podem alterar a textura da gravação | Pode manter mais características da onda original; mudanças grandes ou segmentos mal alinhados podem evidenciar repetição e artefatos de transição |

Esta comparação descreve famílias de técnicas, não uma classificação de qualidade.
O resultado depende da gravação, do `oto.ini`, dos ajustes de pitch e duração e
da implementação de cada motor. WORLD não garante naturalidade, assim como os
métodos que trabalham com a onda original não são automaticamente mais precisos.

## Flags

As letras diferenciam maiúsculas de minúsculas. Os valores são limitados à faixa
aceita pelo motor.

| Flag | Faixa | Efeito |
| --- | ---: | --- |
| `g` | −100 a +100 | Altera o timbre sem mudar a nota. Valores negativos tendem a clarear; positivos, a escurecer. |
| `t` | −100 a +100 | Desloca a curva de pitch em 10 cents por unidade. |
| `B` | 0 a 100 | Aumenta a componente de sopro. |
| `H` | 0 a 99 | Reduz progressivamente as frequências acima do corte. |
| `P` | −100 a +100 | Desloca a posição dos formantes sem mudar o pitch fundamental. |
| `C` | −100 a +100 | Ajusta a região consonantal fixa do `oto.ini`; `0` preserva o valor original. |

Exemplo: `g10B20H0` combina um ajuste de timbre com sopro leve. Flags fora da lista
são ignoradas.

## Como o executável conversa com os editores

O executável recebe os caminhos dos WAVs, a nota, duração, parâmetros temporais,
flags e curva de pitch no formato clássico de resampler. Ele lê WAV PCM de 8, 16,
24 ou 32 bits e WAV IEEE float de 32 bits, converte a entrada para mono e grava a
saída em PCM de 16 bits. O editor fornece os argumentos durante a renderização.

O Tainah aplica nota, curva de pitch, duração, tempos de `oto.ini`, volume e as
flags listadas acima. Os campos clássicos de velocidade, modulação e andamento são
aceitos para manter a chamada compatível, mas ainda não alteram o áudio.

O editor escolhe o alias e a amostra em `oto.ini` e envia os tempos ao Tainah. O
programa não instala nem modifica voicebanks. Se a amostra não tiver cobertura
suficiente ou a análise falhar, o Tainah retorna um erro em vez de criar silêncio.

## Compilar e testar

### Requisitos

- Git com suporte a submódulos;
- Python 3.9 ou posterior;
- CMake 3.16 ou posterior;
- compilador C++17.

Na raiz do repositório, execute:

```sh
python3 build.py
```

O script compila o executável e a biblioteca, executa o teste de ABI e prepara os
arquivos em `build/package/`. Para rodar novamente o teste:

```sh
ctest --test-dir build/engine-build -R tainah_abi --output-on-failure
```

## Biblioteca para integrações

Além do executável, cada pacote inclui uma biblioteca compartilhada com ABI C
versionada. O cabeçalho público está em `src/Tainah/tainah.h`. A chamada principal
é `lt_render`: ela recebe PCM mono `f32`, taxa de amostragem, duração, tempos de
`oto.ini`, flags e pontos de pitch; devolve PCM ou um diagnóstico. Consulte o
cabeçalho para o contrato completo.

### Cache de análise

O Tainah guarda análises WORLD em cache para evitar repetir esse processamento
quando a mesma amostra e as mesmas configurações de análise forem usadas de novo.
Esses arquivos são dados temporários de análise, não arquivos `.frq`, não alteram
o WAV de origem nem o voicebank e podem ser regenerados se estiverem ausentes ou
inválidos.

Por padrão, o cache fica nestes diretórios:

- **Windows:** `%LOCALAPPDATA%\Kamafeu\tainah-analysis`
- **macOS:** `~/Library/Caches/Kamafeu/tainah-analysis`
- **Linux:** `$XDG_CACHE_HOME/kamafeu/tainah-analysis` ou
  `~/.cache/kamafeu/tainah-analysis`

Defina `TAINAH_ANALYSIS_CACHE_DIR` para usar outro diretório.

## Sobre o nome

O nome do programa é **Tainah**. A forma **Tainá** é geralmente associada a
“estrela” ou “estrela da manhã”. O linguista Eduardo de Almeida Navarro, da USP,
apresenta outra origem: Taína, palavra do Nheengatu, com o sentido de “criança”.
Escolhemos a grafia Tainah para o projeto.

## Licença

O projeto é distribuído sob a licença LGPL-3.0-or-later. Consulte [`LICENSE`](LICENSE)
e [`NOTICE.md`](NOTICE.md) para os termos e avisos de autoria.

## Leituras sobre o nome

- [Jornal da USP: entrevista com Eduardo de Almeida Navarro](https://jornal.usp.br/diversidade/etnico-racial/quais-sao-os-nomes-de-origem-indigena-mais-comuns-entre-os-brasileiros/)
- [Artigo na revista Espaço Ameríndio](https://seer.ufrgs.br/EspacoAmerindio/article/view/58713)

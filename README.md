# Tainah

**Resampler vocal com síntese WORLD para UTAU e OpenUtau.**

O Tainah transforma gravações de voicebanks em notas cantadas, ajustando a altura e
a duração. No Windows, funciona com UTAU clássico e OpenUtau. No macOS e Linux, use
o pacote com OpenUtau.

## Baixar

Os pacotes prontos para uso ficam na página [Versões](../../releases/latest):

- **Windows x64:** `Tainah-windows-x64.zip`
- **macOS Apple Silicon:** `Tainah-macos-arm64.zip`
- **Linux x64:** `Tainah-linux-x64.zip`

Extraia o ZIP do seu sistema e mantenha o executável e a biblioteca na mesma pasta.
No Windows, selecione `Tainah.exe` nas configurações de resampler do UTAU ou do
OpenUtau. No macOS e Linux, coloque `Tainah` na pasta de resamplers do OpenUtau e
selecione-o no modo `CLASSIC`. O arquivo `Tainah.yaml` apresenta as quatro flags do
motor no editor de expressões do OpenUtau.

O macOS pode pedir autorização na primeira abertura, pois os pacotes não são
assinados pela Apple. Se isso acontecer, abra **Ajustes do Sistema → Privacidade e
Segurança** e permita a execução do Tainah.

## Recursos

- Analisa a amostra e ressintetiza a voz com WORLD.
- Usa `offset`, `consonant` e `cutoff` recebidos do projeto para respeitar os dados
  de `oto.ini`.
- Mantém o tamanho de saída pedido pelo aplicativo.
- Lê a curva de pitch enviada pelo OpenUtau.
- Oferece as flags `g`, `t`, `B` e `H`.
- Mostra um diagnóstico no terminal quando não consegue abrir, analisar ou
  sintetizar a amostra.

Se a análise WORLD falhar, o Tainah retorna um erro.

## Flags

As letras diferenciam maiúsculas de minúsculas. Os valores são limitados à faixa
aceita pelo motor.

| Flag | Faixa | Efeito |
| --- | ---: | --- |
| `g` | −100 a +100 | Altera o timbre sem mudar a nota. Valores negativos tendem a clarear; positivos, a escurecer. |
| `t` | −100 a +100 | Desloca a curva de pitch em 10 cents por unidade. |
| `B` | 0 a 100 | Aumenta a componente de sopro. |
| `H` | 0 a 99 | Reduz progressivamente as frequências acima do corte. |

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

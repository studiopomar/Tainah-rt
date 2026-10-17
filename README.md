# Tainah

**Biblioteca compartilhada de resampling vocal com análise e síntese WORLD.**

Tainah é uma biblioteca C++ com ABI C versionada, criada para ser carregada por
aplicativos de síntese vocal. No momento, o Kamafeu Studio é seu consumidor
integrado. O projeto não fornece um executável independente que implemente o
protocolo clássico de linha de comando do UTAU.

## Sobre o nome

O motor usa a grafia **Tainah**. A forma do nome mais difundida no Brasil é
**Tainá**, frequentemente traduzida como “estrela” ou “estrela da manhã”. Há,
porém, uma divergência linguística: o linguista Eduardo de Almeida Navarro,
da USP, descreve Tainá como alteração de Taína, do Nheengatu, com o sentido de
“criança”. Por isso, este projeto registra as duas interpretações em vez de
apresentar uma etimologia única como consenso. A grafia Tainah é a identidade
escolhida para o software.

## O que oferece

- análise de F0, envoltória espectral e aperiodicidade com WORLD;
- preservação das regiões de ataque, sustentação e cauda a partir de dados de
  `oto.ini`;
- duração de saída exata, curva completa de pitch e cancelamento por callback;
- parâmetros de voz e flags `g`, `t`, `B` e `H`;
- ABI C versionada, consulta de versão, liberação de PCM e diagnósticos explícitos;
- cache de análise em memória e no diretório de cache do usuário, fora dos
  voicebanks;
- testes de ABI para parâmetros inválidos, cancelamento, cobertura, duração,
  pitch, flags, marcadores, silêncio e invalidação do cache.

Falhas de análise, cobertura insuficiente, síntese inválida ou saída silenciosa
retornam erro. O motor não troca silenciosamente para SOLA ou redimensionamento
de pitch.

## Flags

As flags diferenciam maiúsculas de minúsculas. Valores fora das faixas abaixo
são limitados ao intervalo aceito.

| Flag | Faixa | Efeito |
| --- | ---: | --- |
| `g` | −100 a +100 | Inclina a envoltória espectral, sem alterar a F0. |
| `t` | −100 a +100 | Soma 10 cents por unidade à curva de pitch. |
| `B` | 0 a 100 | Move a aperiodicidade em direção a 0,95. |
| `H` | 0 a 99 | Aplica corte logarítmico na envoltória, de Nyquist até 1 kHz. |

Tokens desconhecidos são ignorados pelo motor e podem ser mantidos pelo
aplicativo hospedeiro para diagnóstico ou compatibilidade.

## Pitch e WORLD

A ABI recebe PCM mono `f32`, taxa de amostragem, duração, parâmetros temporais,
configuração WORLD, flags e pontos de pitch em cents. Cada ponto pode indicar
interpolação suave, linear, ease-in, ease-out ou Hermite. O método de análise
WORLD é Harvest ou DIO. Aplicativos que ofereçam outros trackers devem escolher
um método WORLD compatível ao chamar esta biblioteca.

## Integração com `oto.ini`

O aplicativo hospedeiro resolve alias e carrega a amostra. Tainah recebe a
região PCM e os valores temporais já resolvidos:

- `offset` define o começo útil da amostra;
- `cutoff` limita o final útil;
- marcas de loop/sustain delimitam a região que pode ser estendida;
- a marca de cauda preserva a parte final da amostra;
- a duração solicitada determina o número exato de amostras de saída.

Uma região curta demais ou sem cobertura WORLD suficiente retorna diagnóstico.

## Compilação e testes

### Requisitos

- Git com suporte a submódulos;
- Python 3.9 ou posterior;
- CMake 3.16 ou posterior;
- compilador C++17;
- CTest.

### Compilar a biblioteca e executar CTest

Na raiz do repositório:

```sh
python3 build.py
```

O script obtém a revisão fixada da base de síntese, aplica os arquivos de
integração mantidos neste repositório, compila a biblioteca e executa o teste
de ABI. O artefato e os arquivos temporários são gravados em `build/`.

Para indicar uma cópia local já preparada da base de síntese:

```sh
TAINAH_ENGINE_SOURCE=/caminho/para/a/base python3 build.py
```

Para executar somente o teste novamente após compilar:

```sh
ctest --test-dir build/engine-build -R tainah_abi --output-on-failure
```

O artefato da plataforma é escrito em `build/package/`. Os nomes atuais são
`lessampler_tainah.dll` no Windows, `liblessampler_tainah.dylib` no macOS e
`liblessampler_tainah.so.1` no Linux.

## ABI C

O cabeçalho público está em `src/Tainah/tainah.h`. A versão atual é ABI 2. Os
principais pontos de entrada são:

- `lt_abi_version` e `lt_version` para identificar a biblioteca;
- `lt_render` para renderizar e receber PCM ou diagnóstico;
- `lt_pcm_free` para liberar a saída alocada pela biblioteca;
- `lt_cache_clear_memory` para invalidar o cache em memória.

Estruturas públicas incluem `struct_size` para validação de compatibilidade.
Consulte o cabeçalho para o contrato completo dos parâmetros e formatos.

## Limites e estado

Tainah é destinado a hosts desktop que carregam uma biblioteca compartilhada.
O repositório não instala voicebanks, não distribui amostras ou renders e não
declara validação de qualidade perceptiva. A integração e os pacotes do
Kamafeu são mantidos no repositório daquele aplicativo.

## Licença e avisos

A biblioteca e as modificações cobertas são distribuídas sob LGPL-3.0-or-later.
Consulte [`LICENSE`](LICENSE) e [`NOTICE.md`](NOTICE.md) para os avisos de
copyright e a procedência dos arquivos incorporados.

## Fontes sobre o nome

- [Jornal da USP: entrevista com o linguista Eduardo de Almeida Navarro](https://jornal.usp.br/diversidade/etnico-racial/quais-sao-os-nomes-de-origem-indigena-mais-comuns-entre-os-brasileiros/)
- [Artigo sobre o filme *A Amazônia de Tainá*, na revista Espaço Ameríndio](https://seer.ufrgs.br/EspacoAmerindio/article/view/58713)

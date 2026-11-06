# Máquina de vídeo tutorial de tela (faceless)

Formato modelado nos virais que o Bom selecionou (out/2026): tela real da ferramenta, sem rosto, sem narração,
gancho em texto, passo a passo com legenda palavra por palavra, CTA com palavra-chave para o ManyChat entregar
o material (prompt, lista de códigos, kit) no direct. Música em alta é colocada no app na hora de postar.

## Fluxo de produção (1 vídeo)
1. Pauta: 1 ferramenta (de preferência afiliada) + 1 resultado visível em menos de 30s + 1 isca para o direct.
2. Captura: Claude abre a ferramenta no Chrome do Bom e salva screenshots de cada passo (digitação em 3 quadros).
3. Roteiro: `roteiro.json` (modelo em `exemplos/roteiro-perplexity.json`).
4. Render: `python3 motor/tutorial_tela.py roteiro.json pasta_imagens saida.mp4` (cerca de 5 min para 20s).
5. Conferência: extrair 8 quadros e olhar; checar privacidade (nomes de terceiros e histórico borrados).
6. Entrega: vídeo + legenda + palavra-chave do ManyChat + material da isca.

## Campos do roteiro
- `hook`: linhas do gancho (lista de listas de palavras); `hook_hl`: palavras em amarelo.
- `cta`: `pre`, `kw` (palavra-chave do ManyChat), `pos` (aceita \n).
- `scenes[]`: `d` (segundos), `imgs` (1 ou mais quadros), `b0`/`b1` (enquadramento inicial/final na imagem,
  x0,y0,x1,y1), `blur` (áreas a borrar), `cap`/`sub` (legenda), `hl` (retângulo de destaque), `tap` (toque),
  `stamp` (selo, usado no cold open com o resultado), `cta`, `dim`, `flash`.

## Gancho (abertura)
Nunca repetir a abertura: siga `motor/ganchos.md` e confira com `motor/gancho_check.py`.

## Regras do formato
- Primeiro quadro mostra o RESULTADO (cold open), depois volta para o passo 1.
- Máximo 3 passos. Entre 18 e 30 segundos.
- A palavra-chave do CTA sempre entrega algo concreto (prompt pronto, lista, kit). Os virais analisados
  têm mais comentários que curtidas justamente por causa disso.
- Nunca mostrar nome de empresa ou pessoa real em contexto negativo; borrar.

## Capa padrão (desde 02/11/2026)
Todo vídeo publicado leva capa com a logo do Isso É Dica (identidade visual na grade do perfil).
- Gerar: `python3 motor/capa_gen.py "<titulo da capa>" "<trecho em amarelo>" tutorial/<ID>.capa.jpg`
- Título: a promessa do vídeo em até 7 palavras (não repetir a frase de abertura da narração).
- No pacote `<ID>.json`, grave `"capa": "<ID>.capa.jpg"`. O n8n usa esse campo como capa do Reel no Instagram.
- Sem o campo, o n8n usa `motor/capa_padrao.jpg`.

## Formato Gemini + voz embutida (aprovado pelo Bom em 06/11/2026)
Padrão do tutorial diário a partir de 07/11/2026. Exemplo completo: `teste-gemini/2026-11-06-gemini.*`.
- **Cenas de impacto no Gemini** (cota do plano Pro do Bom, sem custo extra), pelo Chrome dele:
  Nano Banana (Criar imagem, modelo Pro) para imagens e Veo/Omni (Criar vídeo, Retrato 9:16) para 1 clipe por dia.
  Os arquivos baixados caem em `Downloads` do PC do Bom e entram no container com `device_stage_files`.
  Para usar uma imagem gerada como referência do vídeo: botão "Copiar imagem" no chat da imagem, depois Ctrl+V no chat de vídeo.
- **Cena `type: "media"`**: imagem (`img`) ou clipe (`video`, com `vstart`) em tela cheia 9:16, zoom `z0`→`z1`, `focus` [x,y], `blur`, `cap`/`sub`/`stamp`.
- **Narração embutida**: gerar no ElevenLabs (voice_id uWkCxjyU0RSbwgIGZ1dy, modelo `eleven_v4`, 1 take), masterizar com
  `sh motor/voz_master.sh voz.mp3 voz.wav` e passar `"voz": "voz.wav"` no roteiro. O motor mistura a voz com os efeitos.
  Ajuste a duração das cenas aos tempos das frases (`ffmpeg -af silencedetect=n=-38dB:d=0.18`).
  No pacote JSON grave `"narracao_embutida": true` (o n8n então NÃO gera outra voz) e mantenha `narracao` só como registro.
- **Tema visual rotativo**: `python3 motor/tema_pick.py` devolve o tema do dia (nunca repete os últimos 3).
  Grave `"tema"` no roteiro e no pacote. Temas: neon, oceano, brasa, lima, magenta, editorial (cor, fundo,
  estilo de legenda, gancho, transição e inclinação da tela mudam juntos).

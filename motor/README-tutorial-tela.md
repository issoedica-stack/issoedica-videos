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

## Regras do formato
- Primeiro quadro mostra o RESULTADO (cold open), depois volta para o passo 1.
- Máximo 3 passos. Entre 18 e 30 segundos.
- A palavra-chave do CTA sempre entrega algo concreto (prompt pronto, lista, kit). Os virais analisados
  têm mais comentários que curtidas justamente por causa disso.
- Nunca mostrar nome de empresa ou pessoa real em contexto negativo; borrar.

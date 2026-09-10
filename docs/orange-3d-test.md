# Teste refinado da jaqueta laranja

O cartão Solar Orange usa `assets/orange-test/jacket_orange_refined.glb`.
O projeto editável está em `assets/orange-test/jacket_orange_refined.blend`,
na cena `Orange Atelier — Reconstruction`, objeto `Orange_Jacket_Refined`.
O modelo foi construído e atualizado na instância aberta do Blender.

## Melhorias sobre o protótipo rosa

- Uso do canal alfa original, preservando punhos pretos e zíper.
- Remoção de componentes desconectados dos recortes, incluindo pedaços da
  imagem vizinha presentes nas laterais.
- Volume definido pelas quatro vistas cardinais. As quatro diagonais foram
  examinadas como referências, mas não impõem interseções rígidas: suas poses
  e câmeras não correspondem a giros calibrados de 45 graus.
- Abertura geométrica da gola com paredes e interior sombreado.
- Atlas UV único de 2048 px, com mistura gradual de frente, costas e perfis.
- Dilatação das cores a partir do interior do recorte, evitando halos cinzentos.
- Material não metálico com rugosidade própria; iluminação neutra e saída sRGB
  aplicadas exclusivamente ao cartão laranja.

Exportação: 36.000 triângulos, uma malha, um material, aproximadamente 3 MB.
Não foi necessário gerar novas fotografias por IA. As correções necessárias
eram de recorte, geometria e projeção; o interior não observado foi estimado.
As oito referências preparadas estão em `assets/orange-test/reference-*.png`.

## Limitações

É uma reconstrução aproximada, não fotogrametria com câmeras calibradas.
Pode haver distorção ou sobreposição de detalhes na transição entre manga e
corpo. Os reflexos fotografados permanecem na textura, e o interior da gola
é uma aproximação sem referência direta. Avaliar frente, perfil, costas e
três quartos antes de aplicar o método às outras cores.

## Reprodução

1. `python build_orange_hull.py` (Pillow, NumPy, SciPy, scikit-image).
2. No Blender, selecionar uma cena cujo nome comece com `Orange Atelier` e
   executar `build_orange_blender.py` com `__file__` definido para o script.
3. `python bake_orange_atlas.py`.
4. Executar `finish_orange_blender.py` na mesma cena do Blender.
5. Renderizar com Blender em background, abrindo o `.blend` e executando
   `render_orange_previews.py`.

O `.blend` mantém a primeira iteração oculta para comparação. O GLB contém
somente a malha final. A sessão original, que tinha alterações não salvas,
foi preservada em `assets/orange-test/session-before-orange.blend`.

## Verificação

GLB conferido estruturalmente, sintaxe JavaScript validada, carregamento e
arraste testados no site local sem erros de console. Prévia visual conferida
no Blender e no navegador. As demais cores e seus modelos foram preservados.

Teste local: http://127.0.0.1:8088/#collections (servidor `node serve.js`).
Para reverter, restaurar `data-model="assets/jacket_orange.glb"` no cartão
laranja e remover seus atributos `data-preserve-materials` e `data-studio`.

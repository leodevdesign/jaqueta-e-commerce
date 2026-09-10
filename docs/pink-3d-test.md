# Teste da jaqueta rosa

O cartão Neo Magenta usa `assets/pink-test/jacket_pink_test.glb`.
O arquivo editável é `assets/pink-test/jacket_pink_test.blend`.
O GLB rosa anterior e os modelos das outras cores foram preservados.

Reconstrução aproximada por interseção das silhuetas dos oito PNGs
`assets/angulos-3d/jaq-ros-1.png` a `jaq-ros-8.png`. A malha foi suavizada,
reduzida a 26.000 triângulos e exportada no Blender. Frente, costas e laterais
recebem projeções das fotografias. O material original é mantido pelo cartão.

Limitações visuais: as referências não têm câmeras calibradas, portanto as
projeções podem apresentar emendas e distorções. O interior da gola, a separação
interna das mangas e as concavidades não são reconstruídos com precisão.
Os brilhos das fotos permanecem na textura. Este é um protótipo para avaliação,
não uma modelagem de vestuário pronta para fabricação.

Para reproduzir: executar `python build_pink_hull.py` (Pillow, NumPy, SciPy e
scikit-image), depois Blender com `--background --python build_pink_blender.py`.
Os scripts escrevem exclusivamente em `assets/pink-test`.

Para voltar ao modelo anterior: no cartão rosa de `index.html`, restaurar
`data-model="assets/jacket_pink.glb"` e remover `data-preserve-materials`.

Teste local: http://127.0.0.1:8088/#collections (servidor: `node serve.js`).

# Verde: perfil fino e alinhamento corrigido

O cartão Acid Lime agora carrega `assets/green-refined/jacket_green_thin.glb`.
Projeto aberto e salvo: `assets/green-refined/jacket_green_thin.blend`.
Cena: `Green — thin profile refinement`. Objeto final:
`Green_Jacket_Thin_Repaired`. O modelo verde anterior permanece oculto para
comparação na cena e seu GLB original não foi sobrescrito.

Foi mantida a abordagem da verde original: relevo de frente e costas com os
mapas `ver_front_depth.png` e `ver_back_depth.png`. A correção utiliza uma
silhueta comum, alinha escala e altura das costas e ajusta as faixas das mangas.
As bordas são compartilhadas entre as duas superfícies, substituindo as tiras
soltas e a união de máscaras desalinhadas da implementação antiga.

Medidas, em unidades do modelo:

| Modelo | Altura | Profundidade máxima | Profundidade / altura |
|---|---:|---:|---:|
| Verde original | 2,432 | 0,719 | 29,6% |
| Verde corrigida | 2,281 | 0,437 | 19,2% |

A diferença proporcional de espessura é aproximadamente 35%. As medidas são
do protótipo digital, não medidas físicas do produto.

O GLB contém uma malha, dois materiais e 44.498 triângulos, cerca de 1,32 MiB.
Materiais `KHR_materials_unlit` preservam a iluminação já registrada nas fotos.
Somente o cartão verde usa saída sRGB sem tone mapping; os demais não mudaram.

Verificações: zero bordas abertas, zero arestas não manifold, apenas a malha
verde no GLB, extensão unlit presente, sintaxe JS válida, carregamento e arraste
no site local sem erros de console. Prévias de frente, costas, lateral e três
quartos foram renderizadas e inspecionadas.

Limitação: esta é uma malha de relevo fino baseada em fotografias; detalhes
laterais ainda podem apresentar estiramento e emendas, e o interior não é uma
reconstrução física. O objetivo deste teste é avaliar a silhueta fina e o
alinhamento antes de aplicar às outras cores.

Reprodução: `python build_green_refined.py`, executar `finish_green_blender.py`
na cena verde do Blender com `__file__` definido, e renderizar com
`render_green_previews.py`. Bibliotecas: Pillow, NumPy, SciPy, scikit-image.

Reversão: restaurar `data-model="assets/jacket_lime.glb"` no cartão verde e
remover seus atributos `data-preserve-materials` e `data-studio`.

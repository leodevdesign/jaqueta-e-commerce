# Método aprovado da verde aplicado às outras cores

Rosa, laranja e azul usam a construção aprovada da verde: relevo fino de frente
e costas, alinhamento de silhuetas e mangas, bordas compartilhadas e fotografias
sem iluminação adicional. O modelo verde aprovado foi preservado.

| Cor | Pasta | Modelo | Triângulos |
|---|---|---|---:|
| Rosa | assets/pink-thin | jacket_pink_thin.glb | 43.718 |
| Laranja | assets/orange-thin | jacket_orange_thin.glb | 43.650 |
| Azul | assets/blue-thin | jacket_blue_thin.glb | 42.704 |

Cada pasta contém também o `.blend`, texturas, mapas, medições, validação e
prévias de frente, três quartos, perfil e costas. O arquivo azul reúne todas
as cenas finais; cada GLB exporta somente a respectiva jaqueta.

Os mapas são derivados dos PNGs de cada cor pelo mesmo gerador de relevo da
verde. A profundidade é normalizada para a proporção aprovada (~19,2% da altura),
evitando que a luminosidade do pigmento deixe uma jaqueta mais grossa que outra.
Cada cartão usa `data-studio="photographic"` e preserva os materiais unlit.

Validação final: zero bordas abertas ou arestas não manifold; uma malha e dois
materiais unlit por GLB; cerca de 1,3 MiB por arquivo. Carregamento e giro das
três cores conferidos no navegador, sem erros de console. Prévias do Blender
inspecionadas. Mantêm-se as limitações de projeção fotográfica da verde,
incluindo possíveis emendas e estiramento nos perfis.

Reprodução:
1. `python build_thin_colorways.py`.
2. Executar `finish_thin_colorways_blender.py` no Blender com `__file__` definido.
   O script também executa `validate_thin_colorways_blender.py` antes de concluir.
3. Abrir o `.blend` azul em Blender background e executar
   `render_thin_colorways.py` para gerar as prévias.

As versões anteriores em `pink-test`, `orange-test` e os GLBs originais foram
preservados. A integração está nos atributos dos três cartões em `index.html`.

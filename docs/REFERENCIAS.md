# 🧥 Referências de Design - Jaqueta E-Commerce (Techwear / 3D)

Este documento mapeia as referências visuais e a estrutura do site analisadas a partir das capturas de tela salvas em `docs/references/`.

---

## 🎨 Identidade Visual & Estética
- **Estilo**: Cyberpunk / Techwear / Brutalismo Moderno / HUD Futurista / High-End Streetwear.
- **Tema**: Dark mode profundo (`#080808` / `#0D0D0D` / `#000000`) com grid pattern sutil de fundo (pontilhado ou malha técnica).
- **Tipografia**:
  - Títulos: Fonte display em caixa alta com estética técnica/pixelada ou industrial (ex: *PP NeueBit*, *Druk Wide*, *Syne*, *Space Grotesk* ou *Chakra Petch*).
  - Textos de suporte e dados técnicos: Monoespaçada técnica (ex: *JetBrains Mono*, *Geist Mono*, *Space Mono*).
- **Cores de Destaque**:
  - Jaqueta Principal: Efeito metálico furta-cor / iridescente (azul elétrico, roxo, cromo reflexivo).
  - Variações de Coleção: Verde neon (lime), rosa/magenta, laranja tático e azul elétrico.
  - Bordas e divisórias: Linhas finas translúcidas (`rgba(255, 255, 255, 0.12)`), cantoneiras táticas e cruzes/mira estilo HUD militar/técnico (`+`, `[ ]`, `L`).

---

## 📸 Mapeamento das Telas

### 1. `ref-01-hero-jacket-3d.png` - **Hero Section**
- **Header**:
  - Logo estilizado na esquerda (estilo gótico/techwear branding).
  - Navegação central: `SHOP`, `COLLECTIONS`, `TECHNOLOGY`, `ABOUT`.
  - Carrinho no canto direito: `CART [ 0 ]`.
- **Área Central (Hero)**:
  - Render 3D / Modelo interativo flutuante da jaqueta puffer metálica com iluminação dramática e asas/elementos biomecânicos transparentes/metálicos ao fundo.
  - Bloco esquerdo em cantoneira:
    ```
    ┌
      ENGINEERED
      FOR MOTION.
      BUILT TO ENDURE.
    └
    ```
  - Bloco inferior: "WEATHER-RESISTANT. THERMAL INSULATION. OVERSIZED FIT. LIMITED QUANTITY."
  - Call to Action: Botão com moldura tática retangular `[ SHOP NOW ]`.
  - Canto inferior esquerdo: Ícone de globo + "BUILT ON EXPERIENCE. DRIVEN BY INNOVATION. FOCUSED ON YOU." (EST. 202X).

---

### 2. `ref-02-details-matter.png` - **Details Matter (Close-up Interativo)**
- **Título**: `DETAILS MATTER` em tipografia display de alto impacto.
- **Visual**: Close-up na textura, zíperes e materiais da jaqueta 3D.
- **HUD & Especificações Técnicas**:
  - Badges flutuantes sobre o produto.
  - Painel lateral direito com cards de tecnologia do tecido e acabamento.
  - Lista de materiais certificados, resistência a intempéries e acabamento selado.

---

### 3. `ref-03-collections-catalog.png` - **Collections (Grade de Produtos)**
- **Título**: `COLLECTIONS.`
- **Cards de Produto**:
  - Moldura técnica com cantoneiras e numeração (`01`, `02`, `03`, `04`).
  - Efeito hover com rotação do modelo ou zoom.
  - **Modelos**:
    - `01 SHADOW PUFFER JACKET` (Neon Lime) - Preço em destaque ($450).
    - `02 TACTICAL HOODED` (Magenta / Pink) - Preço ($385).
    - `03 THERMAL BOMBER JACKET` (Safety Orange) - Preço ($420).
    - `04 TECH SHELL JACKET` (Cobalt Blue) - Preço ($390).
  - Cada card possui botão de ação rápida (`SHOP NOW` / `VIEW SPECS`).
- **Rodapé da seção**: Botão central `[ VIEW ALL JACKETS ]`.

---

### 4. `ref-04-technology-exploded-layers.png` - **Exploded View (Tecnologia e Camadas)**
- **Título**: `TECHNOLOGY ENGINEERED TO ENDURE`.
- **Visual**:
  - Modelo visual explodido em fatias 3D flutuantes (Outer Shell -> Insulation -> Breathable Membrane -> Inner Lining).
  - Indicadores e linhas conectando cada camada a sua especificação técnica.
- **Copy**:
  - *"EVERY DETAIL HAS A PURPOSE. FROM THE PROTECTIVE OUTER SHELL TO THE INSULATION INSIDE, THE JACKET IS DESIGNED TO PERFORM WITHOUT COMPROMISING ITS FORM."*

---

### 5. `ref-05-faq-specs.png` - **Specs & FAQ ([ALL YOU] NEED TO KNOW)**
- **Título**: `[ALL YOU] NEED TO KNOW.`
- **Layout Split**:
  - Esquerda: Jaqueta flutuando com iluminação atmosférica.
  - Direita: Acordeão com estética de terminal / HUD militar:
    - *How do I choose the right size?*
    - *What materials are used in the jacket?*
    - *How should I care for my jacket?*
    - *Do you ship internationally?*
    - *Can I return or exchange my order?*

---

## 🛠️ Sugestão de Stack para Implementação
- **Framework**: Next.js 14/15 (App Router) ou React + Vite.
- **Estilização**: Tailwind CSS v4 + Lucide Icons + Fontes personalizadas.
- **Animações & Interatividade 3D**:
  - Three.js / React Three Fiber (R3F) / Drei para o modelo 3D interativo da jaqueta.
  - GSAP + ScrollTrigger ou Framer Motion para animações de scroll e transições HUD.
  - Efeito pós-processamento (Bloom, Chromatic Aberration leve, Vignette).

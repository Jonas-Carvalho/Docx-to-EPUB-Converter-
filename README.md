# Docx to EPUB Converter 📚

Aplicativo desktop nativo para Windows compilado em código de máquina via **Nuitka** que transforma documentos do Microsoft Word (`.docx`) em e-books no formato **EPUB 3**, com tipografia otimizada e sumário estruturado para leitores digitais (Kindle, Kobo e Apple Books).

---

## ⚡ Download Rápido (Windows)

Não é necessário instalar Python, configurar dependências ou clonar o projeto. Baixe o executável pré-compilado:

👉 **[Baixar última versão (DocxToEpub.zip)](https://github.com/Jonas-Carvalho/Docx-to-EPUB-Converter-/releases/download/v1.0.0/DocxToEpub.zip)**

### Como Usar:
1. Certifique-se de que o **[Pandoc](https://pandoc.org/installing.html)** está instalado no computador.
2. Descompacte o arquivo `DocxToEpub.zip`.
3. Abra o arquivo executável **`app.exe`** (ou `DocxToEpub.exe`). O aplicativo abrirá diretamente em uma janela nativa do Windows, sem janelas de terminal ou prompt de comando.

---

## 🚀 Funcionalidades

- **Compilação Otimizada (Nuitka):** Executável enxuto e veloz, traduzido diretamente para C/C++ sem o inchaço de ambientes gigantescos.
- **Estruturação Semântica:** Mapeamento automático dos estilos nativos do Word:
  - `Title` $\to$ Capa e título da obra.
  - `Subtitle` $\to$ Subtítulo e crédito de autor.
  - `Heading` $\to$ Capítulos principais (início em nova página com quebra limpa).
  - `Heading 2` $\to$ Subcapítulos aninhados.
  - `Quote` $\to$ Citações em bloco com barra lateral e recuo.
  - `Normal` $\to$ Texto com espaçamento vertical fluído entre parágrafos.
- **Sumário Completo (ToC):** Geração de índice de navegação estruturado nos padrões NCX e NAV XHTML.
- **Hifenização Automática via Soft Hyphens (`\u00ad`):** Separação silábica universal com `pyphen` antes da compilação, garantindo texto perfeitamente justificado sem falhas visuais.
- **Tipografia Fluida:** Folha de estilos CSS minimalista que não trava a fonte, preservando a escolha de tipografia e tamanho de texto no dispositivo do leitor.
- **Imagens Responsivas:** Extração e centralização automática de todas as figuras inseridas no `.docx`.

---

## 📋 Pré-requisitos

1. **Pandoc**: O executável do Pandoc deve estar instalado no sistema e acessível no `PATH`.
   - **Windows:** Baixe pelo site oficial ou use `winget install JohnMacFarlane.Pandoc` / `choco install pandoc`.
   - **macOS:** `brew install pandoc`.
   - **Linux:** `sudo apt-get install pandoc`.
2. **Python 3.10+** *(apenas se for rodar ou compilar a partir do código-fonte)*.

---

## 🛠️ Executando via Código-Fonte

1. Clone o repositório ou baixe o código:
   ```bash
   git clone [https://github.com/Jonas-Carvalho/Docx-to-EPUB-Converter-](https://github.com/Jonas-Carvalho/Docx-to-EPUB-Converter-)
   cd Docx-to-EPUB-Converter-
   ```

2. Crie e ative um ambiente virtual isolado (**obrigatório** para evitar conflitos com pacotes globais ou Anaconda):
   ```bash
   # Windows
   python -m venv venv_limpa
   venv_limpa\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute o aplicativo:
   ```bash
   python app.py
   ```

---

## 📦 Compilação do Executável com Nuitka

O projeto utiliza o **Nuitka** para gerar um binário nativo leve, sem dependências externas de interpretador.

> **Importante:** Sempre realize a compilação com a `venv_limpa` ativa. Compilar a partir de ambientes globais como o Anaconda (`base`) arrastará centenas de megabytes de bibliotecas não utilizadas (como NumPy, SciPy e MKL), inflando desnecessariamente o tamanho do aplicativo.

Com o ambiente virtual ativado e as dependências instaladas:

```bash
python -m nuitka --standalone --windows-disable-console --enable-plugin=pkg-resources --include-data-dir=templates=templates --include-data-dir=static=static --include-package-data=pyphen --output-dir=dist_nuitka app.py
```

### O que o comando faz:
- `--standalone`: Gera uma pasta independente com todas as bibliotecas necessárias para rodar em qualquer máquina Windows.
- `--windows-disable-console`: Remove a janela preta de terminal, exibindo diretamente a interface desktop nativa.
- `--include-data-dir`: Empacota os arquivos de interface (`templates` e `static`).
- `--include-package-data=pyphen`: Inclui os dicionários de hifenização de todos os idiomas.

O executável final estará pronto dentro de **`dist_nuitka/app.dist/app.exe`**.

---

## 📱 Dica de Leitura no Kindle (Via Calibre)

O Kindle não lê arquivos em formato EPUB quando transferidos diretamente por cabo USB. Para manter a hifenização suave e a diagramação impecável ao enviar pelo Calibre:

1. Conecte o Kindle ao computador e abra o **Calibre**.
2. Clique com o botão direito no ícone **Dispositivo** > **Configurar este dispositivo**.
3. Marque **AZW3** e mova-o para o topo da lista de formatos suportados.
4. Em **Preferências** > **Comportamento**, defina o formato de saída preferencial como **AZW3**.
5. Transfira o livro usando o botão **Enviar ao dispositivo**.

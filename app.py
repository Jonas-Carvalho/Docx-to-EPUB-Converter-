import io
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
import pyphen
import webview
from werkzeug.utils import secure_filename

# Compatibilidade de pastas para script Python e PyInstaller
if getattr(sys, "frozen", False):
  template_folder = os.path.join(sys._MEIPASS, "templates")
  static_folder = os.path.join(sys._MEIPASS, "static")
  app = Flask(
      __name__, template_folder=template_folder, static_folder=static_folder
  )
else:
  app = Flask(__name__)

app.secret_key = "chave_secreta_conversor_epub"

ALLOWED_DOC_EXTENSIONS = {"docx"}
ALLOWED_IMG_EXTENSIONS = {"jpg", "jpeg", "png"}


def allowed_file(filename, allowed_set):
  return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


def hyphenate_markdown(text: str, lang_code: str) -> str:
  clean_lang = lang_code.replace("-", "_")
  try:
    dic = pyphen.Pyphen(lang=clean_lang)
  except KeyError:
    try:
      dic = pyphen.Pyphen(lang=clean_lang.split("_")[0])
    except KeyError:
      return text

  word_regex = re.compile(r"([A-Za-zÀ-ÖØ-öø-ÿ\u0400-\u04FF]+)")

  def hyphenate_word(match):
    word = match.group(1)
    if len(word) < 6:
      return word
    return dic.inserted(word, hyphen="\u00ad")

  lines = text.splitlines(keepends=True)
  processed_lines = []

  for line in lines:
    stripped = line.strip()
    if (
        stripped.startswith("#")
        or stripped.startswith("```")
        or stripped.startswith("![")
    ):
      processed_lines.append(line)
    else:
      processed_lines.append(word_regex.sub(hyphenate_word, line))

  return "".join(processed_lines)


@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    language = request.form.get("language", "pt-BR").strip()

    doc_file = request.files.get("doc_file")
    cover_file = request.files.get("cover_file")

    if not doc_file or doc_file.filename == "":
      flash("Envie um arquivo .docx válido.")
      return redirect(url_for("index"))

    if not allowed_file(doc_file.filename, ALLOWED_DOC_EXTENSIONS):
      flash("Apenas arquivos no formato .docx são suportados.")
      return redirect(url_for("index"))

    suggested_filename = (
        f"{secure_filename(title) if title else 'livro'}.epub"
    )

    try:
      with tempfile.TemporaryDirectory() as temp_dir:
        input_docx_path = os.path.join(
            temp_dir, secure_filename(doc_file.filename)
        )
        doc_file.save(input_docx_path)

        extracted_md_path = os.path.join(temp_dir, "content.md")
        hyphenated_md_path = os.path.join(temp_dir, "content_hyphenated.md")
        media_dir = os.path.join(temp_dir, "media")

        # 1. Extração DOCX -> Markdown
        res1 = subprocess.run(
            [
                "pandoc",
                input_docx_path,
                "-o",
                extracted_md_path,
                f"--extract-media={media_dir}",
                "--wrap=none",
            ],
            capture_output=True,
            text=True,
        )
        if res1.returncode != 0:
          raise RuntimeError(f"Erro no Pandoc (Passo 1): {res1.stderr}")

        # 2. Hifenização
        with open(extracted_md_path, "r", encoding="utf-8") as f:
          raw_text = f.read()

        processed_text = hyphenate_markdown(raw_text, language)

        with open(hyphenated_md_path, "w", encoding="utf-8") as f:
          f.write(processed_text)

        output_epub_path = os.path.join(temp_dir, suggested_filename)

        if getattr(sys, "frozen", False):
          css_path = os.path.join(sys._MEIPASS, "static", "epub_style.css")
        else:
          css_path = os.path.abspath(
              os.path.join(app.root_path, "static", "epub_style.css")
          )

        # 3. Compilação EPUB 3
        pandoc_cmd = [
            "pandoc",
            hyphenated_md_path,
            "-f",
            "markdown+raw_html",
            "-o",
            output_epub_path,
            "--to=epub3",
            "--epub-chapter-level=1",
            "--toc",
            "--toc-depth=2",
            f"--css={css_path}",
            f"--metadata=title={title if title else 'Sem Título'}",
            f"--metadata=lang={language}",
            f"--resource-path={temp_dir}",
        ]

        if author:
          pandoc_cmd.append(f"--metadata=author={author}")

        if (
            cover_file
            and cover_file.filename != ""
            and allowed_file(cover_file.filename, ALLOWED_IMG_EXTENSIONS)
        ):
          cover_path = os.path.join(
              temp_dir, secure_filename(cover_file.filename)
          )
          cover_file.save(cover_path)
          pandoc_cmd.append(f"--epub-cover-image={cover_path}")

        res2 = subprocess.run(pandoc_cmd, capture_output=True, text=True)
        if res2.returncode != 0:
          raise RuntimeError(f"Erro no Pandoc (Passo 2): {res2.stderr}")

        # Lê os bytes gerados
        with open(output_epub_path, "rb") as f:
          epub_bytes = f.read()

      # Abre o diálogo nativo do Windows "Salvar como..."
      save_path = None
      if webview.windows:
        dialog_res = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=suggested_filename,
            file_types=("Arquivos EPUB (*.epub)", "Todos os arquivos (*.*)"),
        )
        if dialog_res:
          save_path = (
              dialog_res[0] if isinstance(dialog_res, (list, tuple)) else dialog_res
          )
      else:
        # Fallback caso rode no navegador padrão sem pywebview
        save_path = os.path.join(
            os.path.expanduser("~"), "Downloads", suggested_filename
        )

      if save_path:
        with open(save_path, "wb") as f_out:
          f_out.write(epub_bytes)
        flash(f"✅ Livro gerado e salvo com sucesso em: {save_path}")
      else:
        flash("Operação cancelada pelo usuário.")

      return redirect(url_for("index"))

    except Exception as e:
      flash(f"Erro: {str(e)}")
      return redirect(url_for("index"))

  return render_template("index.html")


def wait_for_server(host="127.0.0.1", port=5000, timeout=10.0):
  start_time = time.time()
  while time.time() - start_time < timeout:
    try:
      with socket.create_connection((host, port), timeout=0.2):
        return True
    except (socket.error, ConnectionRefusedError):
      time.sleep(0.1)
  return False


if __name__ == "__main__":
  HOST = "127.0.0.1"
  PORT = 5000

  server_thread = threading.Thread(
      target=lambda: app.run(
          host=HOST, port=PORT, debug=False, use_reloader=False
      )
  )
  server_thread.daemon = True
  server_thread.start()

  wait_for_server(HOST, PORT)

  webview.create_window(
      title="Docx to EPUB Converter",
      url=f"http://{HOST}:{PORT}",
      width=600,
      height=780,
      resizable=True,
  )
  webview.start()
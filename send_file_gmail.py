#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
#import shutil
import tempfile
import zipfile

def obter_caminho_valido():
    caminho = input("Digite o caminho absoluto do diretório ou arquivo a ser enviado: ")

    while not os.path.exists(caminho):
        print("Caminho inválido. Tente novamente.")
        caminho = input("Digite o caminho absoluto do diretório ou arquivo a ser enviado: ")

    return caminho

def compactar_diretorio(diretorio):
    temp_dir = tempfile.mkdtemp()
    temp_zip = os.path.join(temp_dir, "arquivo.zip")

    with zipfile.ZipFile(temp_zip, 'w') as zipf:
        for raiz, _, arquivos in os.walk(diretorio):
            for arquivo in arquivos:
                caminho_completo = os.path.join(raiz, arquivo)
                relativo = os.path.relpath(caminho_completo, diretorio)
                zipf.write(caminho_completo, relativo)

    return temp_zip

def obter_corpo_email(caminho):
    if os.path.isfile(caminho):
        try:
            with open(caminho, 'r', encoding='utf-8') as arquivo:
                return f"""Olá,

Aqui está o conteúdo do arquivo que você solicitou:

{arquivo.read()}"""
        except UnicodeDecodeError:
            return f"O arquivo não pôde ser decodificado como UTF-8. O conteúdo foi anexado ao e-mail."
    elif os.path.isdir(caminho):
        return f"O caminho fornecido é um diretório. O conteúdo foi compactado e anexado ao e-mail."
    else:
        return "Erro desconhecido ao processar o caminho."


def send_email(remetente_email, remetente_senha, destinatario_email, subject, body, anexo_path=None):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        mensagem = MIMEMultipart()
        mensagem['From'] = remetente_email
        mensagem['To'] = destinatario_email
        mensagem['Subject'] = subject

        mensagem.attach(MIMEText(body, 'plain'))

        if anexo_path:
            with open(anexo_path, 'rb') as anexo:
                anexo_mime = MIMEApplication(anexo.read(), Name=os.path.basename(anexo_path))
                anexo_mime['Content-Disposition'] = f'attachment; filename="{os.path.basename(anexo_path)}"'
                mensagem.attach(anexo_mime)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(remetente_email, remetente_senha)
            server.send_message(mensagem)

        print("Email enviado com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

if __name__ == "__main__":
    remetente_email = "remetente@gmail.com"
    remetente_senha = "yourpass"
    destinatario_email = "destinatario@gmail.com"
    subject = "Sending email through the Python"

    try:
        caminho_arquivo = obter_caminho_valido()

        if os.path.isdir(caminho_arquivo):
            caminho_arquivo = compactar_diretorio(caminho_arquivo)

        corpo_email = obter_corpo_email(caminho_arquivo)

        send_email(remetente_email, remetente_senha, destinatario_email, subject, corpo_email, caminho_arquivo)

    except KeyboardInterrupt:
        print('Encerrando...')

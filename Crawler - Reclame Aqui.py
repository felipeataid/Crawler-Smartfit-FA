import customtkinter
import pandas as pd
import math
import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")

janela = customtkinter.CTk()
janela.geometry("500x300")
janela.minsize(width=500, height=300)
janela.maxsize(width=1000, height=600)

url = "https://www.reclameaqui.com.br/empresa/self-it-academias/lista-reclamacoes"
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}

site = requests.get(url, headers=headers)
soup = BeautifulSoup(site.content, "html.parser")
dialogo = customtkinter.CTkInputDialog

# Botão para puxar as informações do RA
def situacao():
    dialogo = customtkinter.CTkInputDialog(title="Crawler - Situacao RA", text="Insira o link da empresa no Reclame Aqui")
    url_inserido = dialogo.get_input()
    
    print("Começando a colher os dados...")
    chrome = webdriver.Chrome()
    chrome.get(url_inserido)
    chrome.set_window_size(1920,1080)

    # Abrir os dicionários
    dic_situacao = {"TEMPO":[],"SCORE":[], "STATUS":[], "INTERVALO INICIO":[], "INTERVALO FIM":[], "RECLAMACOES RESPONDIDAS":[], "RECLAMACOES TOTAIS":[]}
    
    # Loop em todos os dados da tabela
    for i in range(1, 6):
        chrome.find_element(By.XPATH, f"//*[@id='reputation-tab-{i}']").click()
        tempo = chrome.find_element(By.XPATH, f"//*[@id='reputation-tab-{i}']").text
        score = chrome.find_element(By.XPATH, "//*[@id='reputation']/div[1]/div[1]/div[2]/span[2]").text
        status = chrome.find_element(By.XPATH, "//*[@id='reputation']/div[1]/div[1]/div[2]/span[1]").text
        intervalo_tempo = chrome.find_element(By.XPATH, "//*[@id='reputation']/div[1]/div[1]/div[2]/span[3]").text
        reclamacoes_totais = chrome.find_element(By.XPATH, "//*[@id='reputation']/div[1]/div[2]/a[1]/div/div/b").text
        reclamacoes_respondidas = chrome.find_element(By.XPATH, "//*[@id='reputation']/div[1]/div[2]/a[2]/div/div/b").text

        intervalo_inicio = intervalo_tempo[:-13]
        intervalo_fim = intervalo_tempo[13:]
        score = score.replace('\n', '')

        dic_situacao["TEMPO"].append(tempo)
        dic_situacao["SCORE"].append(score)
        dic_situacao["STATUS"].append(status)
        dic_situacao["INTERVALO INICIO"].append(intervalo_inicio)
        dic_situacao["INTERVALO FIM"].append(intervalo_fim)
        dic_situacao["RECLAMACOES RESPONDIDAS"].append(reclamacoes_respondidas)
        dic_situacao["RECLAMACOES TOTAIS"].append(reclamacoes_totais)
        time.sleep(2)
    chrome.quit
    time.sleep(2)
    dialogo_savecsv = customtkinter.CTkInputDialog(title="Crawler - Situacao RA", text="Digite o nome que será salvo o arquivo CSV...")
    save_csv = str(dialogo_savecsv.get_input()) + ".csv"
    df = pd.DataFrame(dic_situacao)
    df.to_csv(save_csv, encoding="utf-8", sep=";")

def reclamacoes():
    print("Vou colher todos os comentários!")
    url = "https://www.reclameaqui.com.br/empresa/self-it-academias/lista-reclamacoes"
    dialogo_url = customtkinter.CTkInputDialog(title="Crawler - Reclamações de Site", text="Insira o URL do site que você quer extrair as reclamações")
    url = str(dialogo_url.get_input())
    site = requests.get(url, headers=headers)
    soup = BeautifulSoup(site.content, "html.parser")

    # Encontrando a ultima pagina
    total_reclamacoes = soup.find("h1", class_="wydd4i-6 dzEsZn").get_text().strip()
    padrao = r'\d+'
    total_reclamacoes = re.findall(padrao, total_reclamacoes)[-1]
    total = int(total_reclamacoes)
    ultima_pag = math.ceil(int(total)/10)
    dialogo_pag = customtkinter.CTkInputDialog(title="Crawler - Reclamacoes Selfit", text=f"Insira ate qual pagina deseja colher os dados, a ultima página é a {ultima_pag}")
    ultima_pag = int(dialogo_pag.get_input())
    dialogo_time = customtkinter.CTkInputDialog(title="Crawler - Reclamacoes Selfit", text=f"Escolha o intervalo de tempo das requisicoes por página em segundos")
    time_sleep = int(dialogo_time.get_input())

    dic_perguntas = {"pergunta_titulo":[], "pergunta_situacao":[], "pergunta_texto":[], "pergunta_tempo":[], "pergunta_link":[]}
    for i in range(1, ultima_pag+1):
        url_pag = f"https://www.reclameaqui.com.br/empresa/self-it-academias/lista-reclamacoes/?pagina={i}"
        site = requests.get(url_pag, headers=headers)
        soup = BeautifulSoup(site.content, "html.parser")
        perguntas = soup.find_all("div", class_="sc-1pe7b5t-0")
        print(f"Aguardar {time_sleep} segundos...")
        time.sleep(time_sleep)
        print("Continuando...")
        for pergunta in perguntas:
            #perguntas1 = pergunta.find("div", class_="iQGzPh")
            pergunta_titulo = pergunta.find("h4", class_="jAlTVn").get_text()
            pergunta_situacao = pergunta.find("span", class_="sc-1pe7b5t-4").get_text()
            pergunta_texto = pergunta.find("p", class_="jmCUqY").get_text()
            pergunta_tempo = pergunta.find("span", class_="bmtSzo").get_text()
            pergunta_link = pergunta.find("a", href=True)

            dic_perguntas["pergunta_titulo"].append(pergunta_titulo)
            dic_perguntas["pergunta_situacao"].append(pergunta_situacao)
            dic_perguntas["pergunta_texto"].append(pergunta_texto + "...")
            dic_perguntas["pergunta_tempo"].append(pergunta_tempo)
            dic_perguntas["pergunta_link"].append("https://www.reclameaqui.com.br" + pergunta_link["href"])

    dialogo_savecsv = customtkinter.CTkInputDialog(title="Crawler - Situacao RA", text="Digite o nome que será salvo o arquivo CSV...")
    save_csv = str(dialogo_savecsv.get_input()) + ".csv"
    df = pd.DataFrame(dic_perguntas)
    df.to_csv(save_csv, encoding="utf-8", sep=";")

texto = customtkinter.CTkLabel(janela, text="VAMOS AUTOMATIZAR!")
texto.pack(padx=10, pady=10)

botao_situacao = customtkinter.CTkButton(janela, text="EXTRAIR SITUACAO", command=situacao, width=200, height=30)
botao_situacao.pack(padx=15, pady=10)

botao_reclamacoes = customtkinter.CTkButton(janela, text="EXTRAIR RECLAMACOES", command=reclamacoes, width=200, height=30)
botao_reclamacoes.pack(padx=15, pady=10)

janela.mainloop()



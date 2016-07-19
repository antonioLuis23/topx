# topx
Ferramenta Top(x) Web para classificação automática da importância de reviews sobre produtos e serviços.

##Dependencias
MySQL,

Python 3:

  Bibliotecas: nltk, scikit-fuzzy, numpy, matplotlib, django 1.9, BeautifulSoup.

##Instalação:

  1. Com todas as dependencias instaladas, faça o checkout do projeto e no prompt de comando acesse a pasta topxweb.
  
  2. Depois disso rode os comandos: 'python manage.py makemigrations' e 'python manage.py migrate'. Isso vai criar o banco de dados 'comentariostopx' e as tabelas necessárias para o Django. 
  
  3. Após isso rode o comando 'python manage.py createsuperuser' para poder ter acesso a parte de administração.
  
  4. Agora vá dentro da pasta topxweb e rode o arquivo adv_SentilextPT.sql no MySQL para adicionar as tabelas da lista de advérbios e do Sentilex.
  
  5. Depois é so rodar o comando 'python manage.py runserver' e acessar 'localhost:8000/topx/'.

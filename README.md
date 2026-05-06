
---

# ⚡ Banana®Bank MVP (ULTRA RÁPIDO)

🧱 Stack mínima

Streamlit (interface)

SQLite (embutido)

Python 3.10+



---

## 🚀 1. Instalação

```bash
pip install streamlit sqlalchemy passlib
```

---

## 🧠 2. Código completo (1 arquivo só)

Cria um arquivo:

app.py

Cole isso 👇

```python

import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.hash import bcrypt

# DB setup
engine = create_engine("sqlite:///banana_bank.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha = Column(String)
    saldo = Column(Float, default=1000)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    credor_id = Column(Integer)
    devedor_id = Column(Integer)
    valor = Column(Float)
    retorno = Column(Float)
    status = Column(String)

Base.metadata.create_all(engine)

# Auth
def criar_usuario(nome, email, senha):
    user = User(nome=nome, email=email, senha=bcrypt.hash(senha))
    session.add(user)
    session.commit()

def login(email, senha):
    user = session.query(User).filter_by(email=email).first()
    if user and bcrypt.verify(senha, user.senha):
        return user
    return None

# UI
st.title("🍌 Banana®Bank MVP")

menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

if "user" not in st.session_state:
    st.session_state.user = None

# Cadastro
if choice == "Cadastro":
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Criar conta"):
        criar_usuario(nome, email, senha)
        st.success("Conta criada!")

# Login
if choice == "Login":
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = login(email, senha)
        if user:
            st.session_state.user = user
        else:
            st.error("Login inválido")

# Dashboard
if st.session_state.user:
    user = session.query(User).get(st.session_state.user.id)

    st.subheader(f"Bem-vindo, {user.nome}")
    st.write(f"💰 Saldo BNN: {user.saldo}")

    st.divider()

    st.subheader("📤 Criar empréstimo")

    usuarios = session.query(User).filter(User.id != user.id).all()
    user_map = {u.nome: u.id for u in usuarios}

    if usuarios:
        devedor_nome = st.selectbox("Escolher devedor", list(user_map.keys()))
        valor = st.number_input("Valor", min_value=1.0)
        taxa = st.slider("Multiplicador (ex: 2x)", 1.0, 3.0, 2.0)

        if st.button("Criar empréstimo"):
            if user.saldo >= valor:
                loan = Loan(
                    credor_id=user.id,
                    devedor_id=user_map[devedor_nome],
                    valor=valor,
                    retorno=valor * taxa,
                    status="pendente"
                )
                user.saldo -= valor
                session.add(loan)
                session.commit()
                st.success("Empréstimo criado!")
            else:
                st.error("Saldo insuficiente")

    st.divider()

    st.subheader("📥 Empréstimos pendentes")

    loans = session.query(Loan).filter_by(status="pendente", devedor_id=user.id).all()

    for loan in loans:
        credor = session.query(User).get(loan.credor_id)

        st.write(f"De: {credor.nome} | Valor: {loan.valor} | Retorno: {loan.retorno}")

        if st.button(f"Aceitar {loan.id}"):
            user.saldo += loan.valor
            loan.status = "ativo"
            session.commit()
            st.success("Empréstimo aceito!")

    st.divider()

    st.subheader("💳 Pagar empréstimos")

    loans = session.query(Loan).filter_by(status="ativo", devedor_id=user.id).all()

    for loan in loans:
        credor = session.query(User).get(loan.credor_id)

        st.write(f"Para: {credor.nome} | Pagar: {loan.retorno}")

        if st.button(f"Pagar {loan.id}"):
            if user.saldo >= loan.retorno:
                user.saldo -= loan.retorno
                credor.saldo += loan.retorno
                loan.status = "pago"
                session.commit()
                st.success("Pago!")
            else:
                st.error("Saldo insuficiente")
```

---

## ▶️ 3. Rodar o app

```bash
streamlit run app.py
```

---

## 🧪 4. Como testar (fluxo real)

1. Cria 2 usuários


2. Login com usuário A


3. Cria empréstimo


4. Login com usuário B


5. Aceita empréstimo


6. Paga depois



👉 PRONTO: teu sistema já está funcionando


---

## 🔥 5. O que você acabou de criar

Sistema de crédito entre usuários

Moeda interna (BNN simulado)

Multiplicador (teu “dobro”)

Ledger básico


👉 Isso já é um embrião de fintech real


---

## ⚡ 6. Melhorias rápidas (próximo passo)

Se quiser subir o nível HOJE:

Adicionar:

histórico de transações

limite de crédito

score por usuário

upload de arte (simulando NFT)


---

## 🚀 7. Deploy em 10 minutos

Use:

Railway
ou

Render



---

## 🧠 Insight final

Você já não está mais na ideia.

👉 Você tem um produto funcionando

Se rodar isso com teus amigos hoje:

você valida

coleta comportamento

descobre o que realmente importa



---


# 🚀 Banana®Bank PRO (Streamlit)

## 🧱 1. Instalação

```bash
pip install streamlit sqlalchemy passlib pillow pandas
```

---

## 🧠 2. Código PRO (substitui teu app.py)


```python
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.hash import bcrypt
from PIL import Image
import os
import pandas as pd

# --- CONFIG ---
st.set_page_config(page_title="Banana®Bank", layout="wide")

# --- DB ---
engine = create_engine("sqlite:///banana_bank.db")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# --- MODELS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    email = Column(String, unique=True)
    senha = Column(String)
    saldo = Column(Float, default=1000)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True)
    credor_id = Column(Integer)
    devedor_id = Column(Integer)
    valor = Column(Float)
    retorno = Column(Float)
    status = Column(String)

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    nome = Column(String)
    imagem = Column(String)
    valor = Column(Float)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    tipo = Column(String)
    valor = Column(Float)

Base.metadata.create_all(engine)

# --- HELPERS ---
def score_usuario(user_id):
    loans = session.query(Loan).filter_by(devedor_id=user_id).all()
    pagos = [l for l in loans if l.status == "pago"]
    return len(pagos) * 10

def registrar_transacao(user_id, tipo, valor):
    t = Transaction(user_id=user_id, tipo=tipo, valor=valor)
    session.add(t)
    session.commit()

# --- AUTH ---
def criar_usuario(nome, email, senha):
    user = User(nome=nome, email=email, senha=bcrypt.hash(senha))
    session.add(user)
    session.commit()

def login(email, senha):
    user = session.query(User).filter_by(email=email).first()
    if user and bcrypt.verify(senha, user.senha):
        return user
    return None

# --- UI ---
st.title("🍌 Banana®Bank PRO")

if "user" not in st.session_state:
    st.session_state.user = None

menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

# --- CADASTRO ---
if choice == "Cadastro":
    st.subheader("Criar conta")
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        criar_usuario(nome, email, senha)
        st.success("Conta criada!")

# --- LOGIN ---
if choice == "Login":
    st.subheader("Entrar")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Login"):
        user = login(email, senha)
        if user:
            st.session_state.user = user
        else:
            st.error("Erro no login")

# --- DASHBOARD ---
if st.session_state.user:
    user = session.get(User, st.session_state.user.id)

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Saldo", f"{user.saldo:.2f} BNN")
    col2.metric("⭐ Score", score_usuario(user.id))
    col3.metric("📦 Assets", session.query(Asset).filter_by(user_id=user.id).count())

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Empréstimos", "Assets", "Histórico", "Ranking"])

    # --- EMPRÉSTIMOS ---
    with tab1:
        st.subheader("Criar empréstimo")

        usuarios = session.query(User).filter(User.id != user.id).all()
        nomes = {u.nome: u.id for u in usuarios}

        if nomes:
            devedor = st.selectbox("Para quem?", list(nomes.keys()))
            valor = st.number_input("Valor", min_value=1.0)
            taxa = st.slider("Multiplicador", 1.0, 3.0, 1.5)

            if st.button("Emprestar"):
                if user.saldo >= valor:
                    loan = Loan(
                        credor_id=user.id,
                        devedor_id=nomes[devedor],
                        valor=valor,
                        retorno=valor * taxa,
                        status="pendente"
                    )
                    user.saldo -= valor
                    session.add(loan)
                    session.commit()

                    registrar_transacao(user.id, "emprestimo", valor)

                    st.success("Enviado!")

        st.divider()

        st.subheader("Pendentes para você")
        loans = session.query(Loan).filter_by(devedor_id=user.id, status="pendente").all()

        for l in loans:
            credor = session.get(User, l.credor_id)
            st.write(f"{credor.nome} → {l.valor} (pagar {l.retorno})")

            if st.button(f"Aceitar {l.id}"):
                user.saldo += l.valor
                l.status = "ativo"
                session.commit()
                st.success("Aceito")

        st.divider()

        st.subheader("Ativos")
        loans = session.query(Loan).filter_by(devedor_id=user.id, status="ativo").all()

        for l in loans:
            credor = session.get(User, l.credor_id)
            if st.button(f"Pagar {l.id} - {l.retorno}"):
                if user.saldo >= l.retorno:
                    user.saldo -= l.retorno
                    credor.saldo += l.retorno
                    l.status = "pago"
                    session.commit()

                    registrar_transacao(user.id, "pagamento", l.retorno)

                    st.success("Pago!")

    # --- ASSETS ---
    with tab2:
        st.subheader("Seus Assets (NFT fake)")

        uploaded = st.file_uploader("Upload imagem")
        nome = st.text_input("Nome do asset")
        valor = st.number_input("Valor estimado", min_value=0.0)

        if uploaded:
            os.makedirs("uploads", exist_ok=True)
            path = f"uploads/{uploaded.name}"
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())

            if st.button("Salvar asset"):
                asset = Asset(user_id=user.id, nome=nome, imagem=path, valor=valor)
                session.add(asset)
                session.commit()
                st.success("Asset salvo!")

        assets = session.query(Asset).filter_by(user_id=user.id).all()
        for a in assets:
            st.image(a.imagem, width=150)
            st.write(f"{a.nome} - {a.valor} BNN")

    # --- HISTÓRICO ---
    with tab3:
        st.subheader("Transações")

        tx = session.query(Transaction).filter_by(user_id=user.id).all()
        df = pd.DataFrame([{"Tipo": t.tipo, "Valor": t.valor} for t in tx])

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("Sem transações")

    # --- RANKING ---
    with tab4:
        st.subheader("Ranking de usuários")

        users = session.query(User).all()
        ranking = []

        for u in users:
            ranking.append({
                "Nome": u.nome,
                "Score": score_usuario(u.id),
                "Saldo": u.saldo
            })

        df = pd.DataFrame(ranking).sort_values(by="Score", ascending=False)
        st.dataframe(df)

```

---

## 🔥 3. O que essa versão PRO já tem

👉 Isso aqui já parece produto real:

Sistema de crédito funcional

Score automático (gamificação)

Upload de arte (teu “NFT”)

Histórico financeiro

Ranking social (engajamento)

UI organizada em abas


---

## 🧠 4. Como usar estrategicamente

Agora você faz:

1. Convida teus artistas


2. Dá saldo inicial (1000 BNN já está)


3. Observa:

quem paga

quem não paga

comportamento real


👉 Isso vale mais que qualquer plano


---

## 🚀 5. Próximo nível (quando validar)

Depois disso, você pode plugar:

Blockchain (Polygon)

Wallet real

Smart contracts

Token BNN real



---

## 💡 Insight forte

Você acabou de criar:

👉 um laboratório financeiro social

Isso é MUITO mais valioso que sair direto pra cripto.


---



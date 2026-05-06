import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.hash import pbkdf2_sha256
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
    is_admin = Column(Integer, default=0)

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

# --- CREATE ADMIN ---
admin_exists = session.query(User).filter_by(email="admin@banana.com").first()
if not admin_exists:
    admin = User(
        nome="Admin",
        email="admin@banana.com",
        senha=pbkdf2_sha256.hash("admin123"),
        saldo=0,
        is_admin=1
    )
    session.add(admin)
    session.commit()

# --- HELPERS ---
def score_usuario(user_id):
    loans = session.query(Loan).filter_by(devedor_id=user_id).all()
    pagos = [l for l in loans if l.status == "pago"]
    return len(pagos) * 10

def registrar_transacao(user_id, tipo, valor):
    t = Transaction(user_id=user_id, tipo=tipo, valor=valor)
    session.add(t)
    session.commit()

def is_admin(user):
    return user.is_admin == 1

# --- AUTH ---
def criar_usuario(nome, email, senha):
    if len(senha) < 6:
        st.error("Senha deve ter pelo menos 6 caracteres")
        return
    user = User(nome=nome, email=email, senha=pbkdf2_sha256.hash(senha))
    session.add(user)
    session.commit()

def login(email, senha):
    user = session.query(User).filter_by(email=email).first()
    if user and pbkdf2_sha256.verify(senha, user.senha):
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
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        criar_usuario(nome, email, senha)
        st.success("Conta criada!")

# --- LOGIN ---
if choice == "Login":
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

    # --- ADMIN GLOBAL METRICS ---
    if is_admin(user):
        total_users = session.query(User).count()
        total_loans = session.query(Loan).count()
        total_volume = sum([l.valor for l in session.query(Loan).all()])

        st.subheader("📊 Visão Geral")
        c1, c2, c3 = st.columns(3)
        c1.metric("Usuários", total_users)
        c2.metric("Empréstimos", total_loans)
        c3.metric("Volume", f"{total_volume:.2f} BNN")

    # --- USER METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Saldo", f"{user.saldo:.2f} BNN")
    col2.metric("⭐ Score", score_usuario(user.id))
    col3.metric("📦 Assets", session.query(Asset).filter_by(user_id=user.id).count())

    # --- TABS ---
    tabs = ["Empréstimos", "Assets", "Histórico", "Ranking"]
    if is_admin(user):
        tabs.append("Admin")

    tab_objs = st.tabs(tabs)

    # --- EMPRÉSTIMOS ---
    with tab_objs[0]:
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

        st.subheader("Pendentes")
        loans = session.query(Loan).filter_by(devedor_id=user.id, status="pendente").all()
        for l in loans:
            credor = session.get(User, l.credor_id)
            st.write(f"{credor.nome} → {l.valor} (pagar {l.retorno})")
            if st.button(f"Aceitar {l.id}"):
                user.saldo += l.valor
                l.status = "ativo"
                session.commit()
                st.rerun()

        st.subheader("Ativos")
        loans = session.query(Loan).filter_by(devedor_id=user.id, status="ativo").all()
        for l in loans:
            credor = session.get(User, l.credor_id)
            if st.button(f"Pagar {l.id}"):
                if user.saldo >= l.retorno:
                    user.saldo -= l.retorno
                    credor.saldo += l.retorno
                    l.status = "pago"
                    session.commit()
                    registrar_transacao(user.id, "pagamento", l.retorno)
                    st.rerun()

    # --- ASSETS ---
    with tab_objs[1]:
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
                st.success("Salvo!")

        assets = session.query(Asset).filter_by(user_id=user.id).all()
        for a in assets:
            st.image(a.imagem, width=120)
            st.write(a.nome)

    # --- HISTÓRICO ---
    with tab_objs[2]:
        tx = session.query(Transaction).filter_by(user_id=user.id).all()
        df = pd.DataFrame([{"Tipo": t.tipo, "Valor": t.valor} for t in tx])
        st.dataframe(df if not df.empty else pd.DataFrame())

    # --- RANKING ---
    with tab_objs[3]:
        users = session.query(User).all()
        ranking = [{"Nome": u.nome, "Score": score_usuario(u.id)} for u in users]
        df = pd.DataFrame(ranking).sort_values(by="Score", ascending=False)
        st.dataframe(df)

    # --- ADMIN ---
    if is_admin(user):
        with tab_objs[4]:
            st.subheader("Admin")

            users = session.query(User).all()
            for u in users:
                st.write(f"{u.nome} - {u.email} - Saldo: {u.saldo}")
                if st.button(f"Excluir {u.id}"):
                    session.delete(u)
                    session.commit()
                    st.rerun()

            st.subheader("Mint NFT")
            user_map = {u.nome: u.id for u in users}
            dono = st.selectbox("Usuário", list(user_map.keys()))
            nome_asset = st.text_input("Nome NFT")
            valor = st.number_input("Valor NFT", min_value=0.0)
            img = st.file_uploader("Imagem NFT")

            if img:
                path = f"uploads/admin_{img.name}"
                with open(path, "wb") as f:
                    f.write(img.getbuffer())

                if st.button("Mintar"):
                    asset = Asset(
                        user_id=user_map[dono],
                        nome=nome_asset,
                        imagem=path,
                        valor=valor
                    )
                    session.add(asset)
                    session.commit()
                    st.success("Mintado!")

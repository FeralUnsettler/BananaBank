
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
